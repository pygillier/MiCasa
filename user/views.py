from django.views.generic import FormView, TemplateView
from .forms import SetupForm
from django.http import HttpResponseNotFound
from django.contrib.auth import get_user_model
import os


class SetupView(FormView):
    template_name = "user/setup.html"
    form_class = SetupForm

    def dispatch(self, request, *args, **kwargs):
        count = get_user_model().objects.all().count()
        if count > 0:
            return HttpResponseNotFound("Setup already completed.")
        else:
            return super().dispatch(request, *args, **kwargs)


class IndexView(TemplateView):
    template_name = "user/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["current"] = "index"
        return context


class LanguageSelectorView(TemplateView):
    template_name = "user/language.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["redirect_to"] = self.request.path
        context["current"] = "language"
        return context


class AboutView(TemplateView):
    template_name = "user/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        from MiCasa import __version__  # noqa

        context["version"] = __version__

        context["git_commit"] = os.getenv("GIT_COMMIT", "none")

        context["current"] = "about"

        return context
