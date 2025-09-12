# catalog/forms.py
from django import forms
from .models import ProductImage, CarouselBanner
from django.conf import settings

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = "__all__"
        widgets = {
            "image": forms.TextInput(attrs={
                "role": "uploadcare-uploader",
                "data-public-key": settings.UPLOADCARE_PUBLIC_KEY,  # dynamic, not hardcoded
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