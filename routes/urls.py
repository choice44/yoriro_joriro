from django.urls import path
from routes import views

urlpatterns = [
    path("", views.RouteView.as_view(), name="route_view"),
    path("<int:route_id>/", views.RouteDetailView.as_view(),
         name="route_detail_view"),
    path("<int:route_id>/comments/",
         views.CommentView.as_view(), name="comment_view"),
    path("comments/<int:comment_id>/",
         views.CommentDetailView.as_view(), name="comment_detail_view"),
    path("<int:route_id>/rate/", views.RateView.as_view(), name="rate_view")
]
