from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry as registry
from dynamic_preferences.types import StringPreference


general = Section("general")


@registry.register
class SiteTitle(StringPreference):
    section = general
    name = "site_title"
    default = "MiCasa"
    required = False


@registry.register
class DateFormat(StringPreference):
    section = general
    name = "date_format"
    default = "l, j F Y"
    required = False
