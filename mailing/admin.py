from django.contrib import admin

from .models import SubscriberEmail


@admin.register(SubscriberEmail)
class SubscriberEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed", "google_authenticated", "created_at")
    list_filter = ("subscribed", "google_authenticated")
    search_fields = ("email",)
    readonly_fields = ("token", "created_at", "updated_at")
