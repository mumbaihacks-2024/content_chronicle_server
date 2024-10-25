from datetime import datetime, timedelta
from sched import Event

import requests
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from content_chronicle import logger
from main.models import User, Workspace, Post, PostType
from main.serializers.post_serializer import PostSerializer
from main.serializers.user_serializer import UserSerializer
from main.serializers.workspace_serializer import WorkspaceSerializer
import faker


# Create your views here.
class RegisterView(APIView):
    permission_classes = []

    class Serializer(serializers.Serializer):
        username = serializers.CharField()
        email = serializers.EmailField()
        password = serializers.CharField()

        def validate_email(self, value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists")
            return value

        def save(self, **kwargs):
            user = User.objects.create_user(**self.validated_data)
            workspace = Workspace.objects.create(name="Default Workspace", owner=user)
            workspace.members.add(user)
            return user

    def post(self, request):
        serializer = self.Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)

        return Response({"user": user_serializer.data, "token": token.key})


class LoginView(APIView):
    permission_classes = []

    class Serializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def post(self, request):
        serializer = self.Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError(
                {"email": "Email does not exist", "code": "email_not_found"}
            )

        if not user.check_password(serializer.validated_data["password"]):
            raise serializers.ValidationError(
                {"password": "Password is incorrect", "code": "incorrect_password"}
            )

        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)

        return Response({"user": user_serializer.data, "token": token.key})


class UserViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user


class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    lookup_url_kwarg = "workspace_id"

    class AddMemberSerializer(serializers.Serializer):
        email = serializers.EmailField()

    def get_queryset(self):
        return Workspace.objects.filter(
            members__in=[self.request.user]
        ).prefetch_related("members")

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if self.action in ["update", "partial_update", "destroy", "add_member"]:
            if obj.owner != request.user:
                self.permission_denied(
                    request, "You do not have permission to perform this action."
                )

    def create(self, request, *args, **kwargs):
        request.data["owner"] = request.user.id
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        workspace = serializer.save()
        workspace.members.add(self.request.user)

    def add_member(self, request, *args, **kwargs):
        serializer = self.AddMemberSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        workspace = self.get_object()

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User does not exist")

        user = User.objects.get(email=email)
        if workspace.members.filter(id=user.id).exists():
            raise serializers.ValidationError(
                "User is already a member of this workspace"
            )

        workspace.members.add(user)

        return Response(self.serializer_class(workspace).data)


class GenerateEventView(APIView):
    class ParamSerializer(serializers.Serializer):
        custom_instructions = serializers.CharField(
            allow_null=True, allow_blank=True, required=False
        )
        range_start = serializers.DateTimeField(default=datetime.now)
        range_end = serializers.DateTimeField(
            default=lambda: datetime.now() + timedelta(days=7)
        )

    def post(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id)
        serializers = self.ParamSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data
        logger.info(data)
        posts = []
        f = faker.Faker()
        for i in range(5):
            image = requests.get(
                f"https://picsum.photos/1080/720?random={f.pyint(max_value=20)}"
            ).content
            description = f.text(50)
            text = f.text(50)
            schedule_datetime = f.date_time_between(
                data["range_start"], data["range_end"]
            )
            assignee = f.random_element(workspace.members.all())
            post = Post.objects.create(
                description=description,
                schedule_time=schedule_datetime,
                post_image=ContentFile(
                    image, f"{f.pystr(min_chars=5, max_chars=10)}.jpg"
                ),
                post_type=PostType.image,
                post_text=text,
                assignee=assignee,
                workspace=workspace,
                creator=request.user,
            )
            posts.append(post)
        return Response(
            PostSerializer(
                posts, context=self.get_serializer_context(request), many=True
            ).data
        )

    def get_serializer_context(self, request):
        return {
            "request": request,
        }
