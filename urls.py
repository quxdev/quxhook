from .views import WebhookListView
from django.urls import path

urlpatterns = [
    path("webhooks/", WebhookListView.as_view(), name="webhooks"),
]
