import os

from django.core.files.base import ContentFile
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from PIL import Image as PILImage

from weapondetectapp.models import Image, Video, ImagePredict
# from weapondetectapp.utils import TerroristDetector


class ImageListView(LoginRequiredMixin, ListView):
    model = Image, Video
    template_name = "image_list.html"
    context_object_name = "images"

    def get_queryset(self):
        return Image.objects\
            .filter(user=self.request.user)\
            .order_by("-uploaded_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

    def get_success_url(self):
        return reverse_lazy("image-list")


class ImageUploadView(LoginRequiredMixin, CreateView):
    template_name = "image_upload.html"
    model = Image
    fields = ['image']
    success_url = reverse_lazy('image-list')

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.user = self.request.user
        form.instance.name = form.instance.image.name
        images = form.files.getlist("image")
        image_objects = [
            Image(user=self.request.user, image=image, name=image.name)
            for image in images
            if image.name != form.instance.image.name
        ]
        saved_images = Image.objects.bulk_create(image_objects)

        first_file_img_name = form.instance.image.name

        form = super().form_valid(form)

        cur_image = Image.objects.filter(
            user=self.request.user,
            name=first_file_img_name
        ).order_by("-uploaded_at").first()

        image_objects.append(cur_image)

        for image in image_objects:
            abs_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "uploads",
                f"{image.get_path()}"
            )

            image_file = PILImage.open(abs_path)
            content_file = ContentFile(image_file.tobytes())
            cur_image_predict = ImagePredict(
                image_original=image,
                boxes=[],
            )
            cur_image_predict.image_predict.save(
                f"{image.name}",
                content_file
            )
            cur_image_predict.save()

        return form


class VideoUploadView(LoginRequiredMixin, CreateView):
    template_name = "video_upload.html"
    model = Video
    fields = ['video']
    success_url = reverse_lazy('image-list')

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.user = self.request.user
        videos = form.files.getlist("video")
        video_objects = [
            Video(user=self.request.user, video=video)
            for video in videos
            if video.name != form.instance.video.name
        ]
        Video.objects.bulk_create(video_objects)
        return super().form_valid(form)
