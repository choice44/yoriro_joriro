from dataclasses import field
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from users.models import User


# 마이페이지
class MyPageSerializer(serializers.ModelSerializer):
    followings = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    followings_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "area",
            "email",
            "nickname",
            "image",
            "bio",
            "sigungu",
            "gender",
            "age",
            "created_at",
            "updated_at",
            "is_active",
            "is_admin",
            "followers_count",
            "followings_count",
            "followers",
            "followings",
        )

    def get_followings(self, obj):
        followings_data = obj.followings.values("id", "nickname", "image", "email")
        return followings_data

    def get_followers(self, obj):
        followers_data = obj.followers.values("id", "nickname", "image", "email")
        return followers_data

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_followings_count(self, obj):
        return obj.followings.count()


# 마이페이지 수정
class MyPageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "area",
            "nickname",
            "image",
            "bio",
            "sigungu",
            "gender",
            "age",
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


# 회원가입
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user


# 로그인
class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["email"] = user.email
        token["nickname"] = user.nickname

        return token
