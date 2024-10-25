from django.urls import path

from main.views import RegisterView, LoginView

urlpatterns = [
    path("user/register", RegisterView.as_view(), name="register"),
    path("user/login", LoginView.as_view(), name="login"),
]
