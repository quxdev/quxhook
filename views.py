from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import QuxHook
from django.apps import apps


class WebhookListView(TemplateView):
    template_name = "quxhook/quxhook.html"
    app_label = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        confighooks = []
        appconfigs = apps.get_app_configs()
        for app in appconfigs:
            if hasattr(app, "QHOOK_TASKS"):
                confighooks.extend(app.QHOOK_TASKS)

        hooks = []
        for confighook in confighooks:
            hook, status = QuxHook.objects.get_or_create(
                user_slug=self.request.user.profile.slug,
                app=confighook["app"],
                task=confighook["task"],
                event=confighook["event"],
            )
            hooks.append(hook)

        context["webhooks"] = hooks

        print(context)

        return context

    def post(self, request, *args, **kwargs):
        id = request.POST.get("id")
        action_for = request.POST.get("action_for")
        url = request.POST.get("url", None)

        target = QuxHook.objects.get(id=id)
        if action_for == "verify":
            target.url = url
            status, error = target.validate()
        elif action_for == "test_webhook":
            status, error = target.test_webhook()

        return JsonResponse({"status": status, "error": error})
