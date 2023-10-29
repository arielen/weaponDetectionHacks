import os

from django.core.files.base import ContentFile
from django.forms.models import BaseModelForm
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from weapondetectapp.models import Image, Video, ImagePredict, VideoPredict
from weapondetectapp.utils import TerroristDetector


class ImageListView(LoginRequiredMixin, ListView):
    model = Image, ImagePredict
    template_name = "image_list.html"
    context_object_name = "images"

    def get_queryset(self):
        return Image.objects\
            .filter(user=self.request.user)\
            .order_by("-uploaded_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["images_predict"] = ImagePredict.objects.filter(
            image_original__in=self.get_queryset()).order_by("-pk")
        return context

    def get_success_url(self):
        return reverse_lazy("image-list")


class VideoListView(LoginRequiredMixin, ListView):
    model = Video
    template_name = "video_list.html"
    context_object_name = "videos"

    def get_queryset(self):
        return Video.objects\
            .filter(user=self.request.user)\
            .order_by("-uploaded_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["videos_predict"] = VideoPredict.objects.filter(
            video_original__in=self.get_queryset()).order_by("-pk")
        return context

    def get_success_url(self):
        return reverse_lazy("video-list")


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
        Image.objects.bulk_create(image_objects)

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
            with open(abs_path, 'rb') as f:
                content_file = ContentFile(f.read())
                cur_image_predict = ImagePredict(
                    image_original=image,
                    boxes=[],
                )
                cur_image_predict.image_predict.save(
                    f"{image.name}",
                    content_file
                )
                cur_image_predict.save()

            # Отправляем путь изображения в обработчик
            t_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "uploads",
                f"{cur_image_predict.image_predict}"
            )
            print(t_path)
            t = TerroristDetector()
            t.predict_and_draw_boxes_on_existing_image(
                t_path
            )

        return form


class VideoUploadView(LoginRequiredMixin, CreateView):
    template_name = "video_upload.html"
    model = Video
    fields = ['video']
    success_url = reverse_lazy('video-list')

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.user = self.request.user
        form.instance.name = form.instance.video.name
        videos = form.files.getlist("video")
        video_objects = [
            Video(user=self.request.user, video=video, name=video.name)
            for video in videos
            if video.name != form.instance.video.name
        ]
        Video.objects.bulk_create(video_objects)

        first_file_video_name = form.instance.video.name

        form = super().form_valid(form)

        cur_video = Video.objects.filter(
            user=self.request.user,
            name=first_file_video_name
        ).order_by("-uploaded_at").first()

        video_objects.append(cur_video)
        print(video_objects)

        for video in video_objects:
            abs_path = os.path.join(
                os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))),
                "uploads",
                f"{video.video.name}"
            )
            with open(abs_path, 'rb') as f:
                content_file = ContentFile(f.read())
                cur_video_predict = VideoPredict(
                    video_original=video,
                    boxes=[],
                )
                cur_video_predict.video_predict.save(
                    f"{video.name}",
                    content_file
                )
                cur_video_predict.save()

            # Отправляем путь видео в обработчик
            # t_path = os.path.join(
            #     os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            #     "uploads",
            #     f"{cur_image_predict.image_predict}"
            # )
            # print(t_path)
            # t = TerroristDetector()
            # t.predict_and_draw_boxes_on_existing_image(
            #     t_path
            # )
        return form
