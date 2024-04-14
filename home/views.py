from django.views.generic import TemplateView
from constance import config
from weatherapi import WeatherPoint
from .weather import get_icon


class IndexView(TemplateView):
    template_name = "home/index.html"


class WeatherView(TemplateView):
    template_name = "home/weather.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        weatherapi_key = config.WEATHERAPI_KEY
        if weatherapi_key != "":
            enabled = True
            point = WeatherPoint(
                lat=config.WEATHERAPI_LAT,
                lon=config.WEATHERAPI_LON,
            )
            point.set_key(config.WEATHERAPI_KEY)
            point.get_current_weather()

            if config.WEATHERAPI_TEMP == "celsius":
                context["temp"] = f"{point.temp_c}°C"
            else:
                context["temp"] = f"{point.temp_f}°F"

            # Icon
            moment = "day" if point.is_day else "night"
            context["icon"] = get_icon(point.condition_code, moment)

            # Extra coverage
            context["extra"] = f"{getattr(point, config.WEATHERAPI_COVERAGE, 0)}%"

        else:
            enabled = False

        context["weather_enabled"] = enabled

        return context
