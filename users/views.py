from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.decorators import api_view

from users.models import User
from users.serializers import (
    UserSerializer,
    MyPageSerializer,
    LoginSerializer,
)

from django.shortcuts import redirect
from json import JSONDecodeError
from django.http import JsonResponse
import requests
import os
from .models import *
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view


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
    serializer_class = LoginSerializer


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


state = os.environ.get("STATE")
BASE_URL = "http://localhost:8000/"
GOOGLE_CALLBACK_URI = BASE_URL + "users/google/callback/"


# 구글 로그인
class GoogleLoginView(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


@api_view(["POST", "GET"])
def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}"
    )


@api_view(["POST", "GET"])
def google_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get("code")

    # 받은 코드로 구글에 access token 요청
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}"
    )

    # json으로 변환 & 에러 부분 파싱
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    # 에러 발생 시 종료
    if error is not None:
        raise JSONDecodeError(error)

    # 성공 시 access_token 가져오기
    access_token = token_req_json.get("access_token")

    # 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
    )
    email_req_status = email_req.status_code

    if email_req_status != 200:
        return JsonResponse(
            {"err_msg": "failed to get email"}, status=status.HTTP_400_BAD_REQUEST
        )

    # 성공 시 이메일 가져오기
    email_req_json = email_req.json()
    email = email_req_json.get("email")

    # 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
        social_user = SocialAccount.objects.get(user=user)

        # 있는데 구글계정이 아니어도 에러
        if social_user.provider != "google":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이미 Google로 제대로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/google/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "로그인이 실패했습니다."}, status=accept_status)

        user, created = User.objects.get_or_create(email=email)
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/google/login/finish/", data=data)

        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "회원가입이 실패했습니다."}, status=accept_status)

        user, created = User.objects.get_or_create(email=email)
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_201_CREATED,
        )

    except SocialAccount.DoesNotExist:
        # User는 있는데 SocialAccount가 없을 때 (=일반회원으로 가입된 이메일일때)
        return JsonResponse(
            {"err_msg": "email exists but not social user"},
            status=status.HTTP_400_BAD_REQUEST,
        )
