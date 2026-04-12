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
    subscribed = models.BooleanField(default=False)
    google_authenticated = models.BooleanField(default=False)
    token = models.CharField(max_length=24, unique=True, default=generate_token)

    def __str__(self):
        return self.email
