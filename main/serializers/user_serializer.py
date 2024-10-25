from rest_framework import serializers

from main.models import User
from main.serializers.workspace_serializer import WorkspaceSerializer, RemoveFieldSerializer


class UserSerializer(RemoveFieldSerializer):
    workspaces = WorkspaceSerializer(many=True, read_only=True, remove_fields=['members'])

    class Meta:
        model = User
        fields = "__all__"
