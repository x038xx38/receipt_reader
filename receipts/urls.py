from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

app_name = 'receipts'

urlpatterns = [
	# Публичная страница входа. У нее свой, отдельный URL.
	path('login/', LoginView.as_view(
		template_name='receipts/login.html',
		redirect_authenticated_user=True
	), name='login'),

	# URL для выхода. Он просто выполняет выход и перенаправляет на LOGIN_URL.
	path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),

	path('upload-yandex/', views.upload_receipt, name='upload_receipt'),
	path('upload-tesseract/', views.upload_receipt_tesseract, name='upload_receipt_tesseract'),
	path('result/<int:receipt_id>/', views.receipt_result, name='receipt_result'),
	path('history/', views.receipt_history, name='receipt_history'),
]
