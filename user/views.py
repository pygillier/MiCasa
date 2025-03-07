from django.views.generic import FormView, TemplateView, View, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import get_language, gettext_lazy as _
from .forms import SetupForm, DataImportForm
from applications.models import Application
from bookmarks.models import BookmarkCategory
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.conf import settings
import os
import datetime
import logging

logger = logging.getLogger(__name__)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["redirect_to"] = self.request.path
        context["current_language"] = get_language()
        context["version"] = os.getenv("VERSION", "develop")
        context["commit_sha"] = os.getenv("COMMIT_SHA", "offtree")
        context["data_import_form"] = DataImportForm()
        return context


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = "user/login.html"

    success_url = reverse_lazy("user:index")
    success_message = _("user.login.success %(name)s")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Is OIDC support enabled ?
        context["show_oidc_link"] = settings.OIDC_ENABLED

        return context

    def get_success_message(self, cleaned_data):
        user = self.request.user
        return self.success_message % dict(cleaned_data, name=user.first_name if user.first_name else user.username)


class BackupView(LoginRequiredMixin, View):
    """
    Export all user data to a JSON file
    """

    def post(self, request, *args, **kwargs):

        from dynamic_preferences.registries import global_preferences_registry

        registry = global_preferences_registry.manager()

        apps = Application.objects.all()
        cats = BookmarkCategory.objects.prefetch_related("bookmarks").all()  # Prefetch to reduce queries

        response = JsonResponse(
            data={
                "backup_time": datetime.datetime.now().isoformat(),
                "applications": [app.export() for app in apps],
                "bookmarks": [cat.export() for cat in cats],
                "settings": {
                    "language": get_language(),
                    "weather": {
                        "latitude": registry["weather__latitude"],
                        "longitude": registry["weather__longitude"],
                        "temperature": registry["weather__temperature"],
                        "coverage": registry["weather__coverage"],
                    },
                },
            }
        )
        # Force download
        response["Content-Disposition"] = 'attachment; filename="micasa-export.json"'

        return response


class RestoreView(LoginRequiredMixin, RedirectView):
    pattern_name = "user:index"

    def post(self, request, *args, **kwargs):
        logger.info("Starting data restore")

        # Redirect to home with message
        url = self.get_redirect_url(*args, **kwargs)
        return HttpResponseRedirect(url)


class WeatherView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "user/weather.html"
    extra_context = {"current": "weather"}

    success_url = reverse_lazy("user:weather")
    success_message = _("user.manage.weather.success")

    def get_form_class(self):
        from dynamic_preferences.forms import global_preference_form_builder

        return global_preference_form_builder(section="weather")

    def form_valid(self, form):
        form.update_preferences()

        return super().form_valid(form)


class ThemeView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "user/theme.html"
    extra_context = {"current": "theme"}

    success_url = reverse_lazy("user:theme")
    success_message = _("user.manage.theme.success")

    def get_form_class(self):
        from dynamic_preferences.forms import global_preference_form_builder

        return global_preference_form_builder(section="theme")

    def form_valid(self, form):
        form.update_preferences()

        return super().form_valid(form)
