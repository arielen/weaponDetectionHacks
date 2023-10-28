from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from weapondetectapp.models import Image


class ImageListView(LoginRequiredMixin, ListView):
    model = Image
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


class FileUploadView(LoginRequiredMixin, CreateView):
    template_name = "file_upload.html"
    model = Image
    fields = ['image']
    success_url = reverse_lazy('image-list')

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.user = self.request.user
        images = form.files.getlist("image")
        image_objects = [
            Image(user=self.request.user, image=image)
            for image in images
            if image.name != form.instance.image.name
        ]
        Image.objects.bulk_create(image_objects)
        return super().form_valid(form)
