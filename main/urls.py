from django.urls import path

from main.views import RegisterView, LoginView, UserViewset

urlpatterns = [
    path("user/register", RegisterView.as_view(), name="register"),
    path("user/login", LoginView.as_view(), name="login"),
    path("user/update", UserViewset.as_view({"put": "partial_update"}), name="update-user"),
]
