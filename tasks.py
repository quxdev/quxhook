import requests
from celery import shared_task
from django.conf import settings


@shared_task(name="call_target_url", queue="default")
def call_target_url(url, data):
    if settings.DEBUG:
        print(f"== call_target_url(): {data}")

    resp = requests.post(url, json=data)

    if settings.DEBUG:
        print(f"== call_target_url(): response.status_code = {resp.status_code}")
