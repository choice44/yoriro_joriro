from django.urls import path
from recruitments import views

urlpatterns = [
    path("", views.RecruitmentView.as_view(), name="recruitment_view"),
    path("<int:recruitment_id>/", views.RecruitmentDetailView.as_view(), name="recruitment_detail_view"),
    path("<int:recruitment_id>/join/", views.RecruitmentJoinView.as_view(), name="recruitment_join_view")
]
