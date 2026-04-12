from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.socialaccount.urls")),
    path("accounts/", include("allauth.socialaccount.providers.google.urls")),
    path("", include("mailing.urls")),
]
