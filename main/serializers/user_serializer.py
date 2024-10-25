from rest_framework import serializers

from main.models import User
from main.serializers.workspace_serializer import WorkspaceSerializer


class UserSerializer(serializers.ModelSerializer):
    workspaces = WorkspaceSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"
