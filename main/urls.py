from django.urls import path

from main.views import (
    RegisterView,
    LoginView,
    UserViewset,
    WorkspaceViewSet,
    GeneratePostsView,
    RegeneratePost,
    ReminderViewSet,
    PostViewSet,
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
        "workspace/<int:workspace_id>/generate-posts",
        GeneratePostsView.as_view(),
        name="generate-posts",
    ),
    path(
        "workspace/<int:workspace_id>/posts/<int:post_id>/regenerate",
        RegeneratePost.as_view(),
        name="regenerate-post",
    ),
    path(
        "workspace/<int:workspace_id>/posts/<int:post_id>/",
        PostViewSet.as_view(
            {"put": "partial_update", "get": "retrieve", "delete": "destroy"}
        ),
        name="post-detail",
    ),
    path(
        "workspace/<int:workspace_id>/posts/",
        PostViewSet.as_view({"post": "create", "get": "list"}),
        name="post-list",
    ),
    path(
        "workspace/<int:workspace_id>/posts/<int:post_id>/reminders",
        ReminderViewSet.as_view({"post": "create", "get": "list"}),
        name="reminder-list",
    ),
    path(
        "workspace/<int:workspace_id>/posts/<int:post_id>/reminders/<int:reminder_id>",
        ReminderViewSet.as_view({"put": "partial_update", "delete": "destroy"}),
        name="reminder-detail",
    ),
]
