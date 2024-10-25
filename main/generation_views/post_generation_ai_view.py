import json
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from main.generate_post_ai import generate_posts_ai
from main.models import PostGenerationSession, Workspace, Post, PostType
from main.serializers.post_serializer import PostSerializer


class GeneratePostsViewAI(APIView):
    class ParamSerializer(serializers.Serializer):
        custom_instructions = serializers.CharField(
            allow_null=True, allow_blank=True, required=False
        )
        range_start = serializers.DateField(default=lambda: datetime.now().date())
        range_end = serializers.DateField(
            default=lambda: datetime.now().date() + timedelta(days=7)
        )
        session_id = serializers.PrimaryKeyRelatedField(
            queryset=PostGenerationSession.objects.all(),
            required=False,
            allow_null=True,
        )

    def post(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id)
        serializers = self.ParamSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data
        posts = []
        session = data.get(
            "session_id", PostGenerationSession.objects.create(workspace=workspace, creator=request.user)
        )
        response = generate_posts_ai(
            workspace,
            request.user,
            session,
            range_start=data["range_start"].isoformat(),
            range_end=data["range_end"].isoformat(),
            custom_instructions=data.get("custom_instructions"),
        )
        for i in response['response']:
            post = Post.objects.create(
                description=i["descr"],
                img_prompt=i["img_prompt"],
                vid_prompt=i["vid_prompt"],
                schedule_time=i["post_time"],
                assignee_id=i["assignee_id"],
                post_text=i["cap"],
                session=session,
                post_type=PostType.image,
                creator=request.user,
                workspace=workspace,
            )
            posts.append(post)

        return Response(
            PostSerializer(posts, context=self.get_serializer_context(), many=True).data
        )

    def get_serializer_context(self):
        return {"request": self.request}
