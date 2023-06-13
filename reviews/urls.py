from django.urls import path
from reviews import views


urlpatterns = [
    path("", views.ReviewView.as_view(), name="review_view"),
    path("filter/", views.ReviewTypeView.as_view(), name="review_filter_view"),
    path("<int:review_id>/", views.ReviewDetailView.as_view(), name="review_detail_view"),
    path("<int:review_id>/like/", views.ReviewLikeView.as_view(), name="review_like_view"),
]
