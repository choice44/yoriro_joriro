from django.urls import path
from users import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="user_view"),
    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("follow/<int:user_id>/", views.FollowView.as_view(), name="follow_view"),
    path("mypage/<int:user_id>/", views.MyPageView.as_view(), name="mypage_view"),
    path("google/login/", views.google_login, name="google_login"),
    path("google/login/callback/", views.google_callback, name="google_callback"),
    path(
        "google/login/finish/",
        views.GoogleLoginView.as_view(),
        name="google_login_todjango",
    ),
    path("kakao/login/", views.kakao_login, name="kakao_login"),
    path("kakao/login/callback/", views.kakao_callback, name="kakao_callback"),
    path(
        "kakao/login/finish/",
        views.KakaoLoginView.as_view(),
        name="kakao_login_todjango",
    ),
    path("naver/login/", views.naver_login, name="naver_login"),
    path("naver/login/callback/", views.naver_callback, name="naver_callback"),
    path(
        "naver/login/finish/",
        views.NaverLoginView.as_view(),
        name="naver_login_todjango",
    ),
]
