from django.urls import path, include
from users import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("signup/", views.UserView.as_view(), name="user_view"),
    path(
        "login/",
        views.UserTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("follow/<int:user_id>/", views.FollowView.as_view(), name="follow_view"),
    path("<int:user_id>/", views.ProfileView.as_view(), name="profile_view"),
]
