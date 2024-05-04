from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .forms import SetupForm
from applications.models import Application
from bookmarks.models import BookmarkCategory
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
    extra_context = {"current": "index"}


class LanguageSelectorView(TemplateView):
    template_name = "user/language.html"
    extra_context = {"current": "language"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["redirect_to"] = self.request.path
        return context


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = "user/login.html"

    success_url = reverse_lazy("user:index")
    success_message = "user.login.success %(name)s"

    def get_success_message(self, cleaned_data):
        user = self.request.user
        return self.success_message % dict(cleaned_data, name=user.first_name if user.first_name else user.username)


class AboutView(TemplateView):
    template_name = "user/about.html"
    extra_context = {
        "current": "about",
        "versiob": os.getenv("VERSION", "develop"),
        "commit_branch": os.getenv("COMMIT_BRANCH", ""),
        "commit_sha": os.getenv("COMMIT_SHA", ""),
    }


class BackupView(LoginRequiredMixin, TemplateView):
    template_name = "user/backup.html"
    extra_context = {"current": "backup"}

    def post(self, request, *args, **kwargs):
        apps = Application.objects.all()
        cats = BookmarkCategory.objects.all()

        response = render(request, "user/backup.json", {"applications": apps, "categories": cats})

        response["Content-Disposition"] = 'attachment; filename="backup.json"'
        return response
