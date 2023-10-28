from django.contrib.auth.views import LoginView
from django.urls import path, include

from rest_framework import routers

from myauth.views import (
    MyLogoutView,
    RegisterView,
    UserViewSet,
)

app_name = "myauth"

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),

    path("api/", include(router.urls), name="api"),
]
