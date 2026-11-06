from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Anciennes routes
    path("api/users/", include("users.urls")),

    # Nouvelles routes pour React
    path("api/auth/", include("users.urls")),
]