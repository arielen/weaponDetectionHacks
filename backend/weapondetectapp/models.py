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
    name = models.CharField(max_length=255, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name

    def get_path(self):
        return self.image


def images_predict_directory_path(instance: 'ImagePredict', filename: str) -> str:
    return 'images_predict/{0}/{1}'.format(instance.image_original.user.username, filename)


class ImagePredict(models.Model):
    class Meta:
        verbose_name = _('Image Predict')
        verbose_name_plural = _('Images Predict')

    image_original = models.ForeignKey(
        Image, on_delete=models.CASCADE, related_name='image_original')
    image_predict = models.ImageField(upload_to=images_predict_directory_path)
    boxes = models.JSONField(default=list)


def videos_directory_path(instance: 'Video', filename: str) -> str:
    return 'videos/{0}/{1}'.format(instance.user.username, filename)


class Video(models.Model):
    class Meta:
        verbose_name = _('Video')
        verbose_name_plural = _('Videos')

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to=videos_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.video.name
