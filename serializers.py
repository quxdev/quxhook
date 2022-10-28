from rest_framework import serializers

from .models import QuxHook


class QuxHookSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuxHook
        fields = [
            "user",
            "app",
            "task",
            "event",
        ]
