from django.urls import path
from recruitments import views

urlpatterns = [
    path("", views.RecruitmentView.as_view(), name="recruitment_view"),
    path("<int:recruitment_id>/", views.RecruitmentDetailView.as_view(), name="recruitment_detail_view"),
    path("<int:recruitment_id>/join/", views.RecruitmentJoinView.as_view(), name="recruitment_join_view"),
    # path("<int:recruitment_id>/join/<int:applicant_id>/", views.ApplicantAcceptenceView.as_view(), name="applicant_acceptence_view")
    path("<int:recruitment_id>/join/<int:applicant_id>/accept/", views.ApplicantAcceptView.as_view(), name="applicant_accept_view"),
    path("<int:recruitment_id>/join/<int:applicant_id>/reject/", views.ApplicantRejectView.as_view(), name="applicant_reject_view")
]
