from rest_framework import serializers

from main.models import Workspace


class RemoveFieldSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        remove_fields: list | None = kwargs.pop('remove_fields', None)
        super().__init__(*args, **kwargs)

        if remove_fields:
            for field_name in remove_fields:
                if field_name in self.fields:
                    self.fields.pop(field_name)


class WorkspaceSerializer(RemoveFieldSerializer):
    members = serializers.SerializerMethodField()

    def get_members(self, obj):
        from main.serializers.user_serializer import UserSerializer

        return UserSerializer(obj.members.all(), many=True, remove_fields=['workspaces']).data

    class Meta:
        model = Workspace
        fields = "__all__"
