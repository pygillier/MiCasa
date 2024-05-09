import datetime
from django import template
from django.utils.formats import date_format
from dynamic_preferences.registries import global_preferences_registry

register = template.Library()
prefs = global_preferences_registry.manager()


@register.simple_tag
def current_time():
    current_date = datetime.datetime.now()
    return date_format(current_date, format=prefs["general__date_format"], use_l10n=True).capitalize()
