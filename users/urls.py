from django.urls import path, include
from users import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="user_view"),
    path(
        "login/",
        views.LoginView.as_view(),
        name="token_obtain_pair",
    ),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("follow/<int:user_id>/", views.FollowView.as_view(), name="follow_view"),
    path("mypage/<int:user_id>/", views.MyPageView.as_view(), name="mypage_view"),
    path("google/login/", views.google_login, name="google_login"),
    path(
        "google/callback/",
        views.google_callback,
        name="google_callback",
    ),
    path(
        "google/login/finish/",
        views.GoogleLoginView.as_view(),
        name="google_login_todjango",
    ),
]
