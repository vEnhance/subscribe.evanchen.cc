from allauth.socialaccount import views as socialaccount_views
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import RedirectView

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
    path(
        "robots.txt",
        lambda r: HttpResponse("User-agent: *\nAllow: /\n", content_type="text/plain"),
    ),
    path(
        r"favicon.ico",
        RedirectView.as_view(url="https://web.evanchen.cc/favicon.ico"),
    ),
    path("", include("mailing.urls")),
]
