from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("users/", include("users.urls")),
    path("reviews/", include("reviews.urls")),
    path("routes/", include("routes.urls")),
    path("recruitments/", include("recruitments.urls")),
    path("joriro/", include("joriro.urls")),
    path("spots/", include('spots.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
