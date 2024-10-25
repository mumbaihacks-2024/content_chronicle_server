from main.models import Post
from main.serializers.workspace_serializer import RemoveFieldSerializer


class PostSerializer(RemoveFieldSerializer):
    class Meta:
        model = Post
        fields = "__all__"
