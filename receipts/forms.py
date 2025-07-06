from django import forms
from .models import Receipt

class ReceiptUploadForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['original_image']
        widgets = {
            'original_image': forms.FileInput(attrs={'accept': 'image/*'})
        }