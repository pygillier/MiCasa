from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
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


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = "user/login.html"

    success_url = reverse_lazy("user:index")
    success_message = "user.login.success %(name)s"

    def get_success_message(self, cleaned_data):
        user = self.request.user
        return self.success_message % dict(cleaned_data, name=user.first_name if user.first_name else user.username)


class AboutView(TemplateView):
    template_name = "user/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context["version"] = os.getenv("VERSION", "develop")
        context["commit_branch"] = os.getenv("COMMIT_BRANCH", "")
        context["commit_sha"] = os.getenv("COMMIT_SHA", "")

        context["current"] = "about"

        return context
