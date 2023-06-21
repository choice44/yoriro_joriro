from django.urls import path
from joriro import views

urlpatterns = [
    path("", views.JoriroView.as_view(), name="joriro_view"),
]
