from django.urls import path
from weapondetectapp.views import (
    ImageListView,
    FileUploadView,
)

urlpatterns = [
    path("", ImageListView.as_view(), name="image-list"),
    path("upload/", FileUploadView.as_view(), name="upload"),
]
