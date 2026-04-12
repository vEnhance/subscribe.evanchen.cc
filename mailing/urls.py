from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("subscribe/", views.subscribe_form, name="subscribe_form"),
    path(
        "subscribe/<str:token>/",
        views.confirm_subscription,
        name="confirm_subscription",
    ),
    path(
        "unsubscribe/<str:token>/",
        views.unsubscribe_by_token,
        name="unsubscribe_by_token",
    ),
    path("oauth/subscribe/", views.oauth_subscribe, name="oauth_subscribe"),
    path("oauth/unsubscribe/", views.oauth_unsubscribe, name="oauth_unsubscribe"),
    path("done/", views.done, name="done"),
]
