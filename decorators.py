from datetime import datetime

from django.apps import apps

from .models import QuxHook, QuxHookEvent
from .serializers import QuxHookSerializer
from .tasks import call_target_url


def qhook(task, event):
    def wrapper(func):
        def inner(*args, **kwargs):
            hook = kwargs.get("hook", None)

            for k in hook["data"]:
                if k in [x for x in QuxHookEvent.objects.all().values_list("name") if x != event]:
                    hook["data"].pop(k)

            # pre event
            if hook and event == "pre":
                execute_hook(hook, task, event, data=hook["data"])

            data_dict = func(*args, **kwargs)

            # post event
            if hook and event == "post":
                hook["data"]["post"] = data_dict
                execute_hook(hook, task, event, data=hook["data"])

        return inner
    return wrapper


def execute_hook(hook, task, event, data=None):
    if (
        hook["app"] is None
        or task is None
        or event is None
        or hook["user_slug"] is None
        or hook["request_slug"] is None
    ):
        return

    appconfig = apps.get_app_config(hook["app"])
    if hasattr(appconfig, "QUXHOOK_TASKS"):
        found = filter(
            lambda x: x["task"] == task and x["event"] == event, appconfig.QUXHOOK_TASKS
        )
        if not found:
            return

    _hook_target = QuxHook.objects.get_or_none(
        app=hook["app"],
        task=task,
        event=event,
        user_slug=hook["user_slug"],
        is_validated__isnull=False,
    )
    if _hook_target is None:
        return

    hook_out = QuxHookSerializer(_hook_target).data
    hook_out["data"] = data
    hook_out["timestamp"] = datetime.now().isoformat()

    call_target_url.delay(_hook_target.url, hook_out)
