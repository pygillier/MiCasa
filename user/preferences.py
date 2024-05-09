from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry as registry
from dynamic_preferences.types import StringPreference, FloatPreference, ChoicePreference
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

weather = Section("weather")


# WeatherAPI preferences
@registry.register
class WeatherAPIKey(StringPreference):
    section = weather
    name = "apikey"
    verbose_name = _("pref.weather.apikey.verbose_name")
    default = ""
    required = False
    help_text = _("pref.weather.apikey.help")


@registry.register
class WeatherAPILatitude(FloatPreference):
    section = weather
    name = "latitude"
    verbose_name = _("pref.weather.latitude.verbose_name")
    default = 48.8575
    required = False
    help_text = _("pref.weather.latitude.help")

    def validate(self, value):
        if value < -90 or value > 90:
            raise ValidationError("Provided value is outside latitude range (-90, 90)")


@registry.register
class WeatherAPILongitude(FloatPreference):
    section = weather
    name = "longitude"
    verbose_name = _("pref.weather.longitude.verbose_name")
    default = 2.3514
    required = False
    help_text = _("pref.weather.longitude.help")

    def validate(self, value):
        if value < -180 or value > 180:
            raise ValidationError("Provided value is outside latitude range (-180, 180)")


@registry.register
class WeatherAPITempFormat(ChoicePreference):
    section = weather
    name = "temperature"
    verbose_name = _("pref.weather.temperature.verbose_name")
    choices = [("celsius", _("weather.temp.celsius")), ("farenheit", _("weather.temp.farenheit"))]
    default = "celsius"
    required = True
    help_text = _("pref.weather.temperature.help")


@registry.register
class WeatherAPICoverage(ChoicePreference):
    section = weather
    name = "coverage"
    verbose_name = _("pref.weather.coverage.verbose_name")
    choices = [("cloud", _("weather.coverage.cloud")), ("humidity", _("weather.coverage.humidity"))]
    default = "cloud"
    required = True
    help_text = _("pref.weather.coverage.help")
