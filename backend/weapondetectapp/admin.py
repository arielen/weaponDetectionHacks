from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from weapondetectapp.models import Image, ImagePredict


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    list_display = ['user', 'image', 'name', 'uploaded_at']
    list_filter = ['user']
    search_fields = ['user', 'image']
    ordering = ['-uploaded_at']


@admin.register(ImagePredict)
class ImagePredictAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = _('Image Predict')
        verbose_name_plural = _('Images Predict')

    list_display = ['image_original', 'image_predict', 'boxes']
    search_fields = ['image_original', 'image_predict']
