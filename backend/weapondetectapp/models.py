from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


def images_directory_path(instance: 'Image', filename: str) -> str:
    return 'images/{0}/{1}'.format(instance.user.username, filename)


class Image(models.Model):
    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=images_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name
