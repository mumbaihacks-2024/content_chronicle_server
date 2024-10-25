from django.shortcuts import render
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import User
from main.serializers.user_serializer import UserSerializer


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
            return user

    def post(self, request):
        serializer = self.Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)

        return Response({"user": user_serializer.data, "token": token.key})
