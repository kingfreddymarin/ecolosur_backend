# catalog/forms.py
from django import forms
from django.conf import settings
from .models import ProductImage, CarouselBanner

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = "__all__"
        widgets = {
            "image": forms.TextInput(attrs={
                "role": "uploadcare-uploader",
                "data-public-key": settings.UPLOADCARE_PUBLIC_KEY,
            }),
        }

class CarouselBannerForm(forms.ModelForm):
    class Meta:
        model = CarouselBanner
        fields = "__all__"
        widgets = {
            "image": forms.TextInput(attrs={
                "role": "uploadcare-uploader",
                "data-public-key": settings.UPLOADCARE_PUBLIC_KEY,
            }),
        }