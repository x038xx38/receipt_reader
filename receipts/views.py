from .utils import preprocess_image, recognize_text
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
from .forms import ReceiptUploadForm
from .models import Receipt
import pytesseract
import cv2
import numpy as np
from PIL import Image


@login_required
def upload_receipt_tesseract(request):
	if request.method == 'POST':
		form = ReceiptUploadForm(request.POST, request.FILES)
		if form.is_valid():
			receipt = form.save(commit=False)
			receipt.user = request.user
			receipt.status = Receipt.STATUS_PENDING
			receipt.ocr_technology = Receipt.OCR_TESSERACT

			# Сохраняем оригинальное изображение
			receipt.save()

			try:
				# Обрабатываем изображение
				original_path = receipt.original_image.path
				processed_filename = f"processed_{receipt.original_image.name.split('/')[-1].split('.')[0]}.jpg"
				processed_path = os.path.join(settings.MEDIA_ROOT, 'receipts/processed', processed_filename)

				os.makedirs(os.path.dirname(processed_path), exist_ok=True)

				# Чтение изображения
				img = Image.open(original_path)

				# Преобразование в OpenCV формат и предварительная обработка
				img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
				gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
				gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

				# Сохраняем обработанное изображение
				cv2.imwrite(processed_path, gray)
				receipt.processed_image = os.path.join('receipts/processed', processed_filename)

				# Извлечение текста
				text = pytesseract.image_to_string(gray, lang='rus+eng')
				receipt.extracted_text = text
				receipt.status = Receipt.STATUS_SUCCESS

			except Exception as e:
				receipt.status = Receipt.STATUS_ERROR
				receipt.error_message = str(e)

			finally:
				receipt.save()
				return redirect('receipts:receipt_result', receipt_id=receipt.id)
	else:
		form = ReceiptUploadForm()

	return render(request, 'receipts/upload.html', {
		'form': form,
		'description': 'Обработка выполняется с использованием - Tesseract OCR. '
					   'Решение бесплатное, можно попробовать дообучить модель.'
	})


@login_required
def upload_receipt(request):
	if request.method == 'POST':
		form = ReceiptUploadForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				# Создаем объект чека
				receipt = form.save(commit=False)
				receipt.user = request.user
				receipt.status = Receipt.STATUS_PENDING
				receipt.ocr_technology = Receipt.OCR_YANDEX_VISION
				receipt.save()

				# Обработка изображения
				original_path = receipt.original_image.path
				processed_filename = f"processed_{receipt.original_image.name.split('/')[-1].split('.')[0]}.jpg"
				processed_path = os.path.join(settings.MEDIA_ROOT, 'receipts/processed', processed_filename)

				os.makedirs(os.path.dirname(processed_path), exist_ok=True)

				# Предварительная обработка изображения
				if not preprocess_image(original_path, processed_path):
					raise ValueError("Ошибка предварительной обработки изображения")

				receipt.processed_image = os.path.join('receipts/processed', processed_filename)
				receipt.save()

				# Распознавание текста
				try:
					extracted_text = recognize_text(processed_path)
					if not extracted_text:
						raise ValueError("Не удалось распознать текст")

					receipt.extracted_text = extracted_text
					receipt.status = Receipt.STATUS_SUCCESS
					receipt.save()

					return redirect('receipts:receipt_result', receipt_id=receipt.id)

				except Exception as ocr_error:
					receipt.status = Receipt.STATUS_ERROR
					receipt.error_message = f"Ошибка распознавания текста: {str(ocr_error)}"
					receipt.save()
					return redirect('receipts:upload_receipt')

			except Exception as e:
				# Если произошла ошибка на этапе загрузки/обработки
				if receipt.pk:  # Если объект уже сохранен в БД
					receipt.status = Receipt.STATUS_ERROR
					receipt.error_message = str(e)
					receipt.save()

				return redirect('receipts:upload_receipt')

	else:
		form = ReceiptUploadForm()

	return render(request, 'receipts/upload.html', {
		'form': form,
		'description': 'Обработка выполняется с использованием Yandex Vision API для высокоточного распознавания текста. '
					   'Стоимость распознавания одного изображения 13 руб.'
	})


@login_required
def receipt_result(request, receipt_id):
	receipt = Receipt.objects.get(id=receipt_id, user=request.user)
	return render(request, 'receipts/result.html', {'receipt': receipt})


@login_required
def receipt_history(request):
	receipts = Receipt.objects.filter(user=request.user).order_by('-created_at')
	return render(request, 'receipts/history.html', {'receipts': receipts})
