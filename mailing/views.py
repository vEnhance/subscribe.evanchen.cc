from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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
    return render(
        request, "mailing/index.html", {"page_title": "blog.evanchen.cc mailing list"}
    )


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
