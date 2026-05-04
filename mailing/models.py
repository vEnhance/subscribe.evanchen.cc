import secrets
import string

from django.db import models

ALPHABET = string.ascii_letters + string.digits


def generate_token():
    return "".join(secrets.choice(ALPHABET) for _ in range(24))


class SubscriberEmail(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscribed = models.BooleanField(null=True, default=None)
    google_authenticated = models.BooleanField(default=False)
    token = models.CharField(max_length=24, unique=True, default=generate_token)
    name = models.CharField(max_length=255, blank=True)
    custom_greeting = models.TextField(
        blank=True,
        help_text="A customized greeting for the megaphone. "
        "Used to add a personal note to friends.",
    )

    def __str__(self):
        return self.email
