from django.contrib import admin

from .models import SubscriberEmail


@admin.register(SubscriberEmail)
class SubscriberEmailAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "name",
        "subscribed",
        "google_authenticated",
        "created_at",
        "custom_greeting",
    )
    list_filter = ("subscribed", "google_authenticated")
    search_fields = ("email",)
    readonly_fields = ("token", "created_at", "updated_at")
