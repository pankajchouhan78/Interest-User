from rest_framework import serializers
from django.contrib.auth.models import User
from interest_app.models import *


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# #------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ["id", "from_user", "to_user", "message", "created_at", "accepted"]


class SentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ["to_user", "message"]


class AcceptInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ["to_user"]


# class ChatInterestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ChatMessage
#         fields = ['room_name','message','sender']
