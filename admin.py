from .models import *
from django.contrib import admin


class QHookEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "slug",
        "name",
        "description",
        "dtm_created",
        "dtm_updated",
    )


admin.site.register(QuxHookEvent, QHookEventAdmin)
