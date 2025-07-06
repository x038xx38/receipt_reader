from django.contrib import admin
from .models import Receipt

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('extracted_text',)