from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from weapondetectapp.models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    list_display = ['user', 'image', 'uploaded_at']
    list_filter = ['user']
    search_fields = ['user', 'image']
    ordering = ['-uploaded_at']
