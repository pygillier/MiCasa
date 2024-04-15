from django.views.generic import TemplateView
from constance import config
from .weather import get_weather


class IndexView(TemplateView):
    template_name = "home/index.html"


class WeatherView(TemplateView):
    template_name = "home/weather.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        if config.WEATHERAPI_KEY != "":
            enabled = True
            weather = get_weather()
            context.update(weather)
        else:
            enabled = False

        context["weather_enabled"] = enabled

        return context
