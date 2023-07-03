from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import permissions, status

from django.shortcuts import redirect
from django.http import JsonResponse

from dj_rest_auth.registration.views import SocialLoginView

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.naver import views as naver_view

from users.models import User
from users.serializers import (
    UserSerializer,
    MyPageSerializer,
    MyPageUpdateSerializer,
    LoginSerializer,
)

from json import JSONDecodeError

import datetime
import requests
import uuid
import os


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


# 팔로우
class FollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user

        if me == you:
            return Response(
                {"message": "스스로 팔로우할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if me in you.followers.all():
            you.followers.remove(me)
            return Response({"message": "언팔로우하셨습니다."}, status=status.HTTP_200_OK)
        else:
            you.followers.add(me)
            return Response({"message": "팔로우하셨습니다."}, status=status.HTTP_200_OK)


# 마이페이지
class MyPageView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = MyPageSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 마이페이지 수정
    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            serializer = MyPageUpdateSerializer(user, data=request.data, partial=True)
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
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)


# 구글 로그인
state = os.environ.get("STATE")
BASE_URL = "http://localhost:8000/"
GOOGLE_CALLBACK_URI = BASE_URL + "users/google/login/callback/"
GOOGLE_REDIRECT_URI = "http://localhost:5500/users/googleauthcallback/index.html"


class GoogleLoginView(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


@api_view(["POST", "GET"])
def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_REDIRECT_URI}&scope={scope}"
    )


@api_view(["POST", "GET"])
def google_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get("code")

    # 받은 코드로 구글에 access token 요청
    token_request = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_REDIRECT_URI}&state={state}"
    )

    # json으로 변환 & 에러 부분 파싱
    token_request_json = token_request.json()
    error = token_request_json.get("error")

    # 에러 발생 시 종료
    if error is not None:
        raise JSONDecodeError(error)

    # 성공 시 access_token 가져오기
    access_token = token_request_json.get("access_token")

    # 가져온 access_token으로 이메일값을 구글에 요청
    email_request = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
    )
    email_request_status = email_request.status_code

    if email_request_status != 200:
        return JsonResponse(
            {"err_msg": "이메일을 가져오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    # 성공 시 이메일 가져오기
    email_request_json = email_request.json()
    email = email_request_json.get("email")

    profile_request = requests.get(
        f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"
    )
    profile_request_status = profile_request.status_code

    if profile_request_status != 200:
        return JsonResponse(
            {"err_msg": "프로필 정보를 가져오지 못했습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    profile_json = profile_request.json()
    nickname = profile_json.get("name", f"google_user{uuid.uuid4().hex[:8]}")

    # 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
        social_user = SocialAccount.objects.get(user=user)

        # 있는데 구글계정이 아니어도 에러
        if social_user.provider != "google":
            return JsonResponse(
                {"err_msg": "이미 동일한 이메일로 가입한 다른 소셜 계정이 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이미 Google로 제대로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/google/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "로그인이 실패했습니다."}, status=accept_status)

        user, created = User.objects.get_or_create(email=email)
        refresh_token = LoginSerializer.get_token(user)
        access_token = refresh_token.access_token

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
        if User.objects.filter(nickname=nickname):
            user.nickname = nickname + uuid.uuid4().hex[:8]
        else:
            user.nickname = nickname
        user.save()

        refresh_token = LoginSerializer.get_token(user)
        access_token = refresh_token.access_token

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_201_CREATED,
        )

    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"err_msg": "이메일이 있지만 소셜 사용자는 아닙니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


# 카카오 로그인
KAKAO_CALLBACK_URI = BASE_URL + "users/kakao/login/callback/"
KAKAO_REDIRECT_URI = "http://localhost:5500/users/kakaoauthcallback/index.html"


class KakaoLoginView(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    callback_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client


@api_view(["POST", "GET"])
def kakao_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code&scope=account_email"
    )


@api_view(["POST", "GET"])
def kakao_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    code = request.GET.get("code")

    # code로 access token 요청
    token_request = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_REDIRECT_URI}&code={code}"
    )
    token_response_json = token_request.json()

    # 에러 발생 시 중단
    error = token_response_json.get("error", None)
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_response_json.get("access_token")

    # access token으로 카카오 프로필 요청
    profile_request = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()

    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email", None)
    nickname = kakao_account.get("profile", {}).get(
        "nickname", f"kakao_user{uuid.uuid4().hex[:8]}"
    )
    gender = kakao_account.get("gender", None)
    age_range = kakao_account.get("age_range", None)

    if gender:
        if gender == "male":
            gender = "M"
        elif gender == "female":
            gender = "F"
        else:
            gender = None

    if age_range:
        age_min, age_max = age_range.split("~")
        age = int(age_min)
    else:
        age = None

    # 이메일 없으면 오류 => 카카오톡 최신 버전에서는 이메일 없이 가입 가능해서 추후 수정해야함
    if email is None:
        return JsonResponse(
            {"err_msg": "이메일을 가져오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
        social_user = SocialAccount.objects.get(user=user)

        # 있는데 카카오계정이 아니어도 에러
        if social_user.provider != "kakao":
            return JsonResponse(
                {"err_msg": "이미 동일한 이메일로 가입한 다른 소셜 계정이 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이미 카카오로 제대로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "로그인이 실패했습니다."}, status=accept_status)

        user, created = User.objects.get_or_create(email=email)
        refresh_token = LoginSerializer.get_token(user)
        access_token = refresh_token.access_token

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/kakao/login/finish/", data=data)

        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "회원가입이 실패했습니다."}, status=accept_status)

        user, created = User.objects.get_or_create(email=email)
        if User.objects.filter(nickname=nickname):
            user.nickname = nickname + uuid.uuid4().hex[:8]
        else:
            user.nickname = nickname
        user.gender = gender if gender else ""
        user.age = age if age else None
        user.save()

        refresh_token = LoginSerializer.get_token(user)
        access_token = refresh_token.access_token

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_201_CREATED,
        )

    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"err_msg": "이메일이 있지만 소셜 사용자는 아닙니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


# 네이버 로그인
NAVER_CALLBACK_URI = BASE_URL + "users/naver/login/callback/"
NAVER_REDIRECT_URI = "http://localhost:5500/users/naverauthcallback/index.html"


class NaverLoginView(SocialLoginView):
    adapter_class = naver_view.NaverOAuth2Adapter
    callback_url = NAVER_CALLBACK_URI
    client_class = OAuth2Client


@api_view(["POST", "GET"])
def naver_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&state=STATE_STRING&redirect_uri={NAVER_CALLBACK_URI}"
    )


@api_view(["POST", "GET"])
def naver_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_NAVER_SECRET")
    code = request.GET.get("code")
    state_string = request.GET.get("state")

    # code로 access token 요청
    token_request = requests.get(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&state={state_string}&redirect_uri={NAVER_REDIRECT_URI}"
    )
    token_response_json = token_request.json()

    # 에러 발생 시 중단
    error = token_response_json.get("error", None)
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_response_json.get("access_token")

    # access token으로 네이버 프로필 요청
    profile_request = requests.post(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()

    profile_data = profile_json.get("response")

    email = profile_data.get("email")
    nickname = profile_data.get("nickname", f"kakao_user{uuid.uuid4().hex[:8]}")
    gender = profile_data.get("gender", None)
    birthday = profile_data.get("birthday", None)
    birthyear = profile_data.get("birthyear", None)

    if birthday and birthyear:
        current_date = datetime.datetime.now().date()
        birth_date = datetime.datetime.strptime(birthday, "%m-%d").date()
        birth_date = birth_date.replace(year=current_date.year)
        if current_date < birth_date:  # 올해 생일이 지나지 않았을 경우
            age = current_date.year - int(birthyear) - 1
        else:  # 올해 생일이 지났을 경우
            age = current_date.year - int(birthyear)
    else:
        age = None

    if email is None:
        return JsonResponse(
            {"err_msg": "이메일을 가져오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
        social_user = SocialAccount.objects.get(user=user)

        # 있는데 네이버계정이 아니어도 에러
        if social_user.provider != "naver":
            return JsonResponse(
                {"err_msg": "이미 동일한 이메일로 가입한 다른 소셜 계정이 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이미 네이버로 제대로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/naver/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "로그인이 실패했습니다."}, status=accept_status)

        user, created = User.objects.get_or_create(email=email)
        refresh_token = LoginSerializer.get_token(user)
        access_token = refresh_token.access_token

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/naver/login/finish/", data=data)

        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "회원가입이 실패했습니다."}, status=accept_status)

        user, created = User.objects.get_or_create(email=email)
        if User.objects.filter(nickname=nickname):
            user.nickname = nickname + uuid.uuid4().hex[:8]
        else:
            user.nickname = nickname
        user.gender = gender if gender else ""
        user.age = age if age else None
        user.save()

        refresh_token = LoginSerializer.get_token(user)
        access_token = refresh_token.access_token
        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_201_CREATED,
        )

    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"err_msg": "이메일이 있지만 소셜 사용자는 아닙니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )
