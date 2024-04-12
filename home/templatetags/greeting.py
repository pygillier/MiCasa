import datetime
from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.simple_tag
def greeting():
    now = datetime.datetime.now()
    if now.hour >= 18:
        msg = _("greetings.evening")
    elif now.hour >= 12:
        msg = _("greetings.afternoon")
    elif now.hour >= 6:
        msg = _("greetings.morning")
    elif now.hour >= 0:
        msg = _("greetings.night")
    else:
        msg = _("greetings.hello")

    return msg
