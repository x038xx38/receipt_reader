from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Receipt(models.Model):
	# Статусы обработки
	STATUS_PENDING = 'pending'
	STATUS_SUCCESS = 'success'
	STATUS_ERROR = 'error'
	STATUS_CHOICES = [
		(STATUS_PENDING, 'Ожидает обработки'),
		(STATUS_SUCCESS, 'Успешно обработан'),
		(STATUS_ERROR, 'Ошибка обработки'),
	]

	# Технологии OCR
	OCR_TESSERACT = 'tesseract'
	OCR_YANDEX_VISION = 'yandex_vision'
	OCR_CHOICES = [
		(OCR_TESSERACT, 'Tesseract OCR'),
		(OCR_YANDEX_VISION, 'Yandex Vision'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	original_image = models.ImageField(upload_to='receipts/original/')
	processed_image = models.ImageField(upload_to='receipts/processed/', null=True, blank=True)
	extracted_text = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)

	# Новые поля
	status = models.CharField(
		max_length=20,
		choices=STATUS_CHOICES,
		default=STATUS_PENDING
	)
	ocr_technology = models.CharField(
		max_length=20,
		choices=OCR_CHOICES,
		default=OCR_TESSERACT
	)
	error_message = models.TextField(blank=True, null=True)  # Для сохранения ошибок

	def __str__(self):
		return f"Receipt {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')} ({self.status})"

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Чек'
		verbose_name_plural = 'Чеки'