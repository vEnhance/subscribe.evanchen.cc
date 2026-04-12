from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.httip import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from postmarker.core import PostmarkClient

from .forms import EmailSubscribeForm
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


def subscribe_form(request):
    if not settings.POSTMARK_API_KEY:
        return HttpResponse("Currently not available", status=503)
    if request.method == "POST":
        form = EmailSubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            obj, _ = SubscriberEmail.objects.get_or_create(email=email)
            if obj.subscribed is not None:
                _send_confirmation_email(email, obj.token, request)
            return render(
                request,
                "mailing/confirmation_sent.html",
                {"page_title": "Check your email"},
            )
    else:
        form = EmailSubscribeForm()
    return render(
        request,
        "mailing/subscribe_form.html",
        {"page_title": "Subscribe", "form": form},
    )


def confirm_subscription(request, token):
    try:
        obj = SubscriberEmail.objects.get(token=token)
    except SubscriberEmail.DoesNotExist:
        return render(request, "mailing/bad_token.html", {"page_title": "Link invalid"})
    if request.method == "POST":
        obj.subscribed = True
        obj.save()
        return _render_done(request, "subscribed", obj.email)
    return _render_confirm(request, "subscribe", obj.email)


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


def _send_confirmation_email(email, token, request):
    if not settings.POSTMARK_API_KEY:
        raise PermissionDenied
    client = PostmarkClient(server_token=settings.POSTMARK_API_KEY)
    confirm_url = request.build_absolute_uri(
        reverse("confirm_subscription", args=[token])
    )
    unsub_url = request.build_absolute_uri(
        reverse("unsubscribe_by_token", args=[token])
    )
    client.emails.send(
        From=settings.POSTMARK_FROM_EMAIL,
        To=email,
        Subject="Confirm your subscription to blog.evanchen.cc",
        TextBody=(
            "Someone (hopefully you) asked to subscribe to blog.evanchen.cc."
            f"Click the link below to confirm your subscription:\n{confirm_url}\n\n"
            f"To unsubscribe later, visit:\n{unsub_url}"
        ),
        HtmlBody=(
            "<p>Someone (hopefully you) asked to subscribe to blog.evanchen.cc.</p>"
            f'<p><a href="{confirm_url}">Confirm subscription</a></p>'
            f'<p>Later on, you can use <a href="{unsub_url}">unsubscribe here</a></p>'
        ),
    )
