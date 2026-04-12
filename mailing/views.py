from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from postmarker.core import PostmarkClient

from .forms import EmailSubscribeForm
from .models import SubscriberEmail


def index(request):
    return render(request, "mailing/index.html")


def subscribe_form(request):
    if request.method == "POST":
        form = EmailSubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            obj, _ = SubscriberEmail.objects.get_or_create(email=email)
            if obj.subscribed:
                return render(
                    request,
                    "mailing/done.html",
                    {"action": "already_subscribed", "email": email},
                )
            _send_confirmation_email(email, obj.token, request)
            return render(request, "mailing/confirmation_sent.html")
    else:
        form = EmailSubscribeForm()
    return render(request, "mailing/subscribe_form.html", {"form": form})


def confirm_subscription(request, token):
    try:
        obj = SubscriberEmail.objects.get(token=token)
    except SubscriberEmail.DoesNotExist:
        return render(
            request, "mailing/error.html", {"message": "Invalid or expired link."}
        )
    if request.method == "POST":
        obj.subscribed = True
        obj.save()
        return render(
            request, "mailing/done.html", {"action": "subscribed", "email": obj.email}
        )
    return render(
        request,
        "mailing/confirm_action.html",
        {"action": "subscribe", "email": obj.email},
    )


def unsubscribe_by_token(request, token):
    try:
        obj = SubscriberEmail.objects.get(token=token)
    except SubscriberEmail.DoesNotExist:
        return render(
            request, "mailing/error.html", {"message": "Invalid or expired link."}
        )
    if request.method == "POST":
        obj.subscribed = False
        obj.save()
        return render(
            request, "mailing/done.html", {"action": "unsubscribed", "email": obj.email}
        )
    return render(
        request,
        "mailing/confirm_action.html",
        {"action": "unsubscribe", "email": obj.email},
    )


@login_required
def oauth_subscribe(request):
    email = request.user.email
    obj, _ = SubscriberEmail.objects.get_or_create(email=email)
    obj.subscribed = True
    obj.google_authenticated = True
    obj.save()
    return render(
        request, "mailing/done.html", {"action": "subscribed", "email": email}
    )


@login_required
def oauth_unsubscribe(request):
    email = request.user.email
    try:
        obj = SubscriberEmail.objects.get(email=email)
        obj.subscribed = False
        obj.save()
        action = "unsubscribed"
    except SubscriberEmail.DoesNotExist:
        action = "not_found"
    return render(request, "mailing/done.html", {"action": action, "email": email})


def _send_confirmation_email(email, token, request):
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
        Subject="Confirm your subscription",
        TextBody=(
            f"Click the link below to confirm your subscription:\n{confirm_url}\n\n"
            f"To unsubscribe later, visit:\n{unsub_url}"
        ),
        HtmlBody=(
            f'<p><a href="{confirm_url}">Confirm subscription</a></p>'
            f'<p><a href="{unsub_url}">Unsubscribe</a></p>'
        ),
    )
