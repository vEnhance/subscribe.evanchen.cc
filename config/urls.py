from allauth.socialaccount import views as socialaccount_views
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/login/cancelled/",
        socialaccount_views.login_cancelled,
        name="socialaccount_login_cancelled",
    ),
    path(
        "accounts/login/error/",
        socialaccount_views.login_error,
        name="socialaccount_login_error",
    ),
    path(
        "accounts/signup/",
        socialaccount_views.signup,
        name="socialaccount_signup",
    ),
    path("accounts/", include("allauth.socialaccount.providers.google.urls")),
    path("", include("mailing.urls")),
]
