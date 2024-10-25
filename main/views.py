from django.shortcuts import render
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from main.models import User, Workspace
from main.serializers.user_serializer import UserSerializer
from main.serializers.workspace_serializer import WorkspaceSerializer


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
    lookup_url_kwarg = 'workspace_id'

    class AddMemberSerializer(serializers.Serializer):
        email = serializers.EmailField()

    def get_queryset(self):
        return Workspace.objects.filter(members__in=[self.request.user]).prefetch_related('members')

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
            raise serializers.ValidationError("User is already a member of this workspace")

        workspace.members.add(user)

        return Response(self.serializer_class(workspace).data)
