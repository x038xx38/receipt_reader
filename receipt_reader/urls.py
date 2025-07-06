from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from receipts import views

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', views.upload_receipt, name='home'),
	path('users/', TemplateView.as_view(template_name='receipts/users.html'), name='users'),
	path('extract/', TemplateView.as_view(template_name='receipts/extract.html'), name='extract'),
	path('orders/', TemplateView.as_view(template_name='receipts/orders.html'), name='orders'),

	path('receipts/', include('receipts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
			+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)