from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils.timezone import now

from .models import SubscriberEmail

_DONE_TITLES = {
    "subscribed": "Subscribed",
    "unsubscribed": "Unsubscribed",
    "already_subscribed": "Already subscribed",
    "not_found": "Not found",
}

_CONFIRM_TITLES = {
    "subscribe": "Confirm subscription",
    "unsubscribe": "Confirm unsubscription",
}


def index(request):
    return render(request, "mailing/index.html", {"page_title": "Evan's mailing list"})


def unsubscribe_by_token(request, token):
    try:
        obj = SubscriberEmail.objects.get(token=token)
    except SubscriberEmail.DoesNotExist:
        return render(request, "mailing/bad_token.html", {"page_title": "Link invalid"})
    if request.method == "POST":
        obj.subscribed = False
        obj.save()
        return _render_done(request, "unsubscribed", obj.email)
    return _render_confirm(request, "unsubscribe", obj.email)


@login_required
def oauth_subscribe(request):
    email = request.user.email
    if request.method == "POST":
        obj, _ = SubscriberEmail.objects.get_or_create(email=email)
        obj.subscribed = True
        obj.google_authenticated = True
        if not obj.name:
            obj.name = request.user.get_full_name()
        obj.save()
        return _render_done(request, "subscribed", email)
    elif SubscriberEmail.objects.filter(email=email, subscribed=True).exists():
        return _render_done(request, "already_subscribed", email)

    return _render_confirm(request, "subscribe", email)


@login_required
def oauth_unsubscribe(request):
    email = request.user.email
    if request.method == "POST":
        try:
            obj = SubscriberEmail.objects.get(email=email)
            obj.subscribed = False
            obj.save()
            action = "unsubscribed"
        except SubscriberEmail.DoesNotExist:
            action = "not_found"
        return _render_done(request, action, email)
    return _render_confirm(request, "unsubscribe", email)


def _render_done(request, action, email):
    return render(
        request,
        "mailing/done.html",
        {
            "page_title": _DONE_TITLES.get(action, "Done"),
            "action": action,
            "email": email,
        },
    )


def _render_confirm(request, action, email):
    return render(
        request,
        "mailing/confirm_action.html",
        {
            "page_title": _CONFIRM_TITLES[action],
            "action": action,
            "email": email,
        },
    )


def subscriber_list(request: HttpRequest) -> JsonResponse:
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    expected_hash = settings.SUBSCRIBER_LIST_TOKEN_HASH
    if not expected_hash:
        return JsonResponse({"error": "API not configured"}, status=503)
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    provided_token = auth_header[len("Bearer ") :]
    if not check_password(provided_token, expected_hash):
        return JsonResponse({"error": "Forbidden"}, status=403)
    subscribers = list(
        SubscriberEmail.objects.filter(subscribed=True).values(
            "email", "token", "name", "custom_greeting"
        )
    )
    return JsonResponse({"timestamp": now().isoformat(), "subscribers": subscribers})
