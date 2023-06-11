from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from users.models import User
from users.serializers import (
    UserSerializer,
    MyPageSerializer,
    UserTokenObtainPairSerializer,
)


# 회원가입
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입 완료!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


# 로그인
class LoginView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer


# 팔로우
class FollowView(APIView):
    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user

        if me == you:
            return Response(
                {"message": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if me in you.followers.all():
            you.followers.remove(me)
            return Response({"message": "unfollow"}, status=status.HTTP_200_OK)
        else:
            you.followers.add(me)
            return Response({"message": "follow"}, status=status.HTTP_200_OK)


# 마이페이지
class MyPageView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = MyPageSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 마이페이지 수정
    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "마이페이지 수정 완료!"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    # 회원 탈퇴
    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            user.is_active = False
            user.save()
            return Response({"message": "회원 탈퇴 완료!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)
