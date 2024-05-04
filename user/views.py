from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
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


class IndexView(LoginRequiredMixin, TemplateView):
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


class UserLoginView(LoginView):
    template_name = "user/login.html"

    def get_success_url(self):
        return reverse_lazy("user:index")


class AboutView(TemplateView):
    template_name = "user/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context["version"] = os.getenv("VERSION", "develop")
        context["commit_branch"] = os.getenv("COMMIT_BRANCH", "")
        context["commit_sha"] = os.getenv("COMMIT_SHA", "")

        context["current"] = "about"

        return context
