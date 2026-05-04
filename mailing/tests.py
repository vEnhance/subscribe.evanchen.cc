import pytest
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.urls import reverse

from .models import SubscriberEmail


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="pw"
    )


@pytest.fixture
def subscriber(db):
    return SubscriberEmail.objects.create(email="test@example.com")


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


# --- index ---


def test_index(client, db):
    resp = client.get(reverse("index"))
    assert resp.status_code == 200


# --- unsubscribe_by_token ---


def test_unsubscribe_get_valid_token(client, subscriber):
    resp = client.get(reverse("unsubscribe_by_token", args=[subscriber.token]))
    assert resp.status_code == 200
    assert resp.context["action"] == "unsubscribe"


def test_unsubscribe_get_bad_token(client, db):
    resp = client.get(reverse("unsubscribe_by_token", args=["x" * 24]))
    assert resp.status_code == 200
    assert "bad_token" in resp.templates[0].name


def test_unsubscribe_post_valid_token(client, subscriber):
    subscriber.subscribed = True
    subscriber.save()
    resp = client.post(reverse("unsubscribe_by_token", args=[subscriber.token]))
    assert resp.status_code == 200
    assert resp.context["action"] == "unsubscribed"
    subscriber.refresh_from_db()
    assert subscriber.subscribed is False


def test_unsubscribe_post_bad_token(client, db):
    resp = client.post(reverse("unsubscribe_by_token", args=["x" * 24]))
    assert resp.status_code == 200
    assert "bad_token" in resp.templates[0].name


# --- oauth_subscribe ---


def test_oauth_subscribe_requires_login(client, db):
    resp = client.get(reverse("oauth_subscribe"))
    assert resp.status_code == 302


def test_oauth_subscribe_get_new(auth_client, db):
    resp = auth_client.get(reverse("oauth_subscribe"))
    assert resp.status_code == 200
    assert resp.context["action"] == "subscribe"


def test_oauth_subscribe_get_already_subscribed(auth_client, user):
    SubscriberEmail.objects.create(email=user.email, subscribed=True)
    resp = auth_client.get(reverse("oauth_subscribe"))
    assert resp.status_code == 200
    assert resp.context["action"] == "already_subscribed"


def test_oauth_subscribe_post_creates(auth_client, user, db):
    resp = auth_client.post(reverse("oauth_subscribe"))
    assert resp.status_code == 200
    assert resp.context["action"] == "subscribed"
    obj = SubscriberEmail.objects.get(email=user.email)
    assert obj.subscribed is True
    assert obj.google_authenticated is True


def test_oauth_subscribe_post_updates(auth_client, user):
    SubscriberEmail.objects.create(email=user.email, subscribed=False)
    auth_client.post(reverse("oauth_subscribe"))
    obj = SubscriberEmail.objects.get(email=user.email)
    assert obj.subscribed is True
    assert obj.google_authenticated is True


# --- oauth_unsubscribe ---


def test_oauth_unsubscribe_requires_login(client, db):
    resp = client.get(reverse("oauth_unsubscribe"))
    assert resp.status_code == 302


def test_oauth_unsubscribe_get(auth_client, db):
    resp = auth_client.get(reverse("oauth_unsubscribe"))
    assert resp.status_code == 200
    assert resp.context["action"] == "unsubscribe"


def test_oauth_unsubscribe_post_existing(auth_client, user):
    SubscriberEmail.objects.create(email=user.email, subscribed=True)
    resp = auth_client.post(reverse("oauth_unsubscribe"))
    assert resp.status_code == 200
    assert resp.context["action"] == "unsubscribed"
    obj = SubscriberEmail.objects.get(email=user.email)
    assert obj.subscribed is False


def test_oauth_unsubscribe_post_not_found(auth_client, db):
    resp = auth_client.post(reverse("oauth_unsubscribe"))
    assert resp.status_code == 200
    assert resp.context["action"] == "not_found"


# --- subscriber_list API ---


_TOKEN = "testtoken"
_TOKEN_HASH = make_password(_TOKEN)


def test_subscriber_list_no_auth(client, db, settings):
    settings.SUBSCRIBER_LIST_TOKEN_HASH = _TOKEN_HASH
    resp = client.get(reverse("subscriber_list"))
    assert resp.status_code == 401


def test_subscriber_list_wrong_token(client, db, settings):
    settings.SUBSCRIBER_LIST_TOKEN_HASH = _TOKEN_HASH
    resp = client.get(
        reverse("subscriber_list"),
        HTTP_AUTHORIZATION="Bearer wrongtoken",
    )
    assert resp.status_code == 403


def test_subscriber_list_returns_subscribed_only(client, db, settings):
    settings.SUBSCRIBER_LIST_TOKEN_HASH = _TOKEN_HASH
    SubscriberEmail.objects.create(email="yes@example.com", subscribed=True)
    SubscriberEmail.objects.create(email="no@example.com", subscribed=False)
    SubscriberEmail.objects.create(email="null@example.com", subscribed=None)
    resp = client.get(
        reverse("subscriber_list"),
        HTTP_AUTHORIZATION=f"Bearer {_TOKEN}",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "timestamp" in data
    subscribers = data["subscribers"]
    assert len(subscribers) == 1
    assert subscribers[0]["email"] == "yes@example.com"
    assert len(subscribers[0]["token"]) == 24


def test_subscriber_list_post_not_allowed(client, db, settings):
    settings.SUBSCRIBER_LIST_TOKEN_HASH = _TOKEN_HASH
    resp = client.post(
        reverse("subscriber_list"),
        HTTP_AUTHORIZATION=f"Bearer {_TOKEN}",
    )
    assert resp.status_code == 405


# --- model ---


def test_token_generated_automatically(db):
    obj = SubscriberEmail.objects.create(email="auto@example.com")
    assert len(obj.token) == 24
    assert obj.token.isalnum()


def test_tokens_are_unique(db):
    a = SubscriberEmail.objects.create(email="a@example.com")
    b = SubscriberEmail.objects.create(email="b@example.com")
    assert a.token != b.token
