from datetime import datetime

import requests
from django.db import models
from django.utils.crypto import get_random_string

from qux.models import CoreModel, default_null_blank

"""
QuxHook object that registers the app name and the hooks with names and related tasks and events
"""


class QuxHookEvent(CoreModel):
    slug = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=16)
    description = models.CharField(max_length=64, **default_null_blank)


class QuxHook(CoreModel):
    slug = models.CharField(max_length=8, unique=True)
    user = models.CharField(max_length=32)
    app = models.CharField(max_length=32)
    task = models.CharField(max_length=64)
    event = models.ForeignKey(QuxHookEvent, on_delete=models.DO_NOTHING)
    url = models.URLField()
    secret = models.CharField(max_length=16, **default_null_blank)
    is_validated = models.DateTimeField(**default_null_blank)

    class Meta:
        unique_together = ("user", "app", "task", "event")
        db_table = "quxhook"
        verbose_name = "QuxHook"
        verbose_name_plural = "QuxHooks"

    # generate secret_key before save if not exist
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.secret = get_random_string(16)
        super().save(*args, **kwargs)

    # remove QuxHook
    @classmethod
    def remove(cls, slug):
        try:
            cls.objects.get(slug=slug).delete()
            return True
        except cls.DoesNotExist:
            raise cls.DoesNotExist

    def __str__(self):
        return self.slug

    # call url in the hook and expect secret as response
    def validate(self):
        try:
            response = requests.get(self.url, verify=True)
        except requests.exceptions.SSLError as e:
            print("Website does not support https.\n")
            print(str(e))
            return False, "ERR_SSL_PROTOCOL_ERROR"

        response_text = response.text.strip('"')

        if str(response_text) == str(self.secret):
            self.is_validated = datetime.now()
            self.save()
            return True, None

        # response does not match the secret
        return False, None

    def test_webhook(self):
        url = self.url
        data = {
            "app": self.app,
            "task": self.task,
            "event": self.event,
            "secret": self.secret,
        }
        if url:
            response = requests.post(url, data=data)

            if response.status_code == 200:
                return True, "Posted test data successfully"
            else:
                return False, "Could not post test data to the url!!"

        return False, "URL not entered!!"
