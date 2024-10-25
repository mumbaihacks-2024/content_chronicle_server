from django.urls import path

from main.views import (
    RegisterView,
    LoginView,
    UserViewset,
    WorkspaceViewSet,
    GenerateEventView,
)

urlpatterns = [
    path("user/register", RegisterView.as_view(), name="register"),
    path("user/login", LoginView.as_view(), name="login"),
    path(
        "user/update",
        UserViewset.as_view({"put": "partial_update"}),
        name="update-user",
    ),
    path(
        "workspace/<int:workspace_id>/",
        WorkspaceViewSet.as_view(
            {"put": "partial_update", "get": "retrieve", "delete": "destroy"}
        ),
        name="workspace-view",
    ),
    path(
        "workspace/",
        WorkspaceViewSet.as_view({"post": "create", "get": "list"}),
        name="update-workspace",
    ),
    path(
        "workspace/<int:workspace_id>/add-member",
        WorkspaceViewSet.as_view({"post": "add_member"}),
        name="create-workspace",
    ),
    path(
        "workspace/<int:workspace_id>/generate-events",
        GenerateEventView.as_view(),
        name="generate-events",
    ),
]
