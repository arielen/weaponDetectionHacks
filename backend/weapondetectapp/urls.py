from django.urls import path
from weapondetectapp.views import (
    ImageListView,
    ImageUploadView,
    VideoUploadView,
)

urlpatterns = [
    path("", ImageListView.as_view(), name="image-list"),
    path("upload_image/", ImageUploadView.as_view(), name="upload-image"),
    path("upload_video/", VideoUploadView.as_view(), name="upload-video"),
]
