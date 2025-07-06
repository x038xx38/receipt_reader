import base64
import requests
import json
from PIL import Image
from django.conf import settings
import os


def preprocess_image(input_path, output_path, max_size_kb=1024, quality=85, max_width=2000):
    """Обработка изображения перед отправкой в API"""
    try:
        img = Image.open(input_path)
        if img.width > max_width:
            w_percent = max_width / float(img.width)
            h_size = int(float(img.height) * float(w_percent))
            img = img.resize((max_width, h_size), Image.LANCZOS)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.save(output_path, 'jpeg', quality=quality, optimize=True)
        print(f"Изображение обработано: {output_path}")
        return True
    except Exception as e:
        print(f"Ошибка обработки изображения: {e}")
        return False

def recognize_text(image_path, folder_id=settings.YANDEX_FOLDER_ID, api_key_secret=settings.YANDEX_API_KEY):
    """Отправляет изображение в Yandex Vision и возвращает текст с сохранением структуры."""
    with open(image_path, "rb") as f:
        image_data = f.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')

    body = {
        "folderId": folder_id,
        "analyze_specs": [{
            "content": base64_image,
            "features": [{
                "type": "TEXT_DETECTION",
                "text_detection_config": {
                    "language_codes": ["*"]
                }
            }]
        }]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key_secret}"
    }

    try:
        response = requests.post(
            "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze",
            headers=headers,
            json=body
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {e}"

    try:
        result_json = response.json()
    except ValueError:
        return "Ошибка: неверный JSON в ответе"

    try:
        # Словарь для группировки строк по Y-координате
        lines_dict = {}

        for result in result_json.get("results", []):
            for res in result.get("results", []):
                if "textDetection" in res:
                    for page in res["textDetection"].get("pages", []):
                        for block in page.get("blocks", []):
                            for line in block.get("lines", []):
                                # Получаем среднюю Y-координату строки
                                vertices = line["boundingBox"]["vertices"]
                                y_position = sum(int(v["y"]) for v in vertices) / 4

                                # Ключ для группировки - округленная Y-координата
                                line_key = int(round(y_position / 10) * 10)

                                line_text = " ".join(
                                    word.get("text", "")
                                    for word in line.get("words", [])
                                )

                                # Группируем текст с одинаковыми Y-координатами
                                if line_key not in lines_dict:
                                    lines_dict[line_key] = []
                                lines_dict[line_key].append(line_text)

        # Объединяем текст на одной строке
        merged_lines = []
        for y_pos in sorted(lines_dict.keys()):
            merged_line = " ".join(lines_dict[y_pos])
            merged_lines.append((y_pos, merged_line))

        # Сортируем строки по Y-позиции и формируем итоговый текст
        merged_lines.sort(key=lambda x: x[0])
        receipt_text = "\n".join(line[1] for line in merged_lines)

        if not receipt_text.strip():
            return "Текст не распознан. Полный ответ:\n" + json.dumps(result_json, indent=2)

        return receipt_text

    except Exception as e:
        return (f"Ошибка обработки: {e}\nПолный ответ:\n" +
                json.dumps(result_json, indent=2, ensure_ascii=False))