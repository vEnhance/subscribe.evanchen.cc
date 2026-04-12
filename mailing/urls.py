from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.subscribe_form, name="subscribe_form"),
    path(
        "add/<str:token>/",
        views.confirm_subscription,
        name="confirm_subscription",
    ),
    path(
        "remove/<str:token>/",
        views.unsubscribe_by_token,
        name="unsubscribe_by_token",
    ),
    path("oauth/subscribe/", views.oauth_subscribe, name="oauth_subscribe"),
    path("oauth/unsubscribe/", views.oauth_unsubscribe, name="oauth_unsubscribe"),
]
