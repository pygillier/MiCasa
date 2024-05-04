from django.forms import ModelForm, Select, TextInput
from .models import Application
from django.utils.translation import gettext as _


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ["name", "description", "url", "icon", "is_public"]
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": _("apps.manage.form.name.placeholder")}),
            "description": TextInput(
                attrs={"class": "form-control"},
            ),
            "url": TextInput(
                attrs={"class": "form-control", "placeholder": "https://"},
            ),
            "is_public": Select(
                attrs={"class": "form-select"},
                choices={True: _("apps.manage.form.is_public.public"), False: _("apps.manage.form.is_public.private")},
            ),
        }
        labels = {
            "name": _("apps.manager.form.name.label"),
            "description": _("apps.manager.form.description.label"),
            "url": _("apps.manager.form.url.label"),
            "icon": _("apps.manager.form.icon.label"),
            "is_public": _("apps.manager.form.is_public.label"),
        }
        help_texts = {
            "icon": _("apps.manager.form.icon.help_text"),
            "description": _("apps.manager.form.description.help_text"),
            "is_public": _("apps.manager.form.is_public.help_text"),
        }
