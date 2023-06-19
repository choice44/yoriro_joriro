from django.urls import path
from spots import views

urlpatterns = [
    path("", views.SpotFilterView.as_view(), name="spot_view"),
    path("<int:spot_id>/", views.SpotDetailView.as_view(), name="spot_detail_view"),
    path("area/", views.AreaView.as_view(), name="area_view"),
    path("area/<int:area_id>/", views.SigunguView.as_view(), name="sigungu_view"),
]
