from django.views.generic import TemplateView
from dynamic_preferences.registries import global_preferences_registry
from .weather import get_weather


registry = global_preferences_registry.manager()


class IndexView(TemplateView):
    template_name = "home/index.html"


class WeatherView(TemplateView):
    template_name = "home/weather.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        if registry["weather__apikey"].strip() != "":
            enabled = True
            weather = get_weather()
            context.update(weather)
        else:
            enabled = False

        context["weather_enabled"] = enabled

        return context
