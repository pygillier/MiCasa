from django.forms import ModelForm, Select, TextInput, URLInput
from .models import Application
from django.utils.translation import gettext_lazy as _


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ["name", "description", "url", "icon", "is_public", "is_pinned"]
        widgets = {
            "name": TextInput(attrs={"id": "app_name", "placeholder": _("apps.manage.form.name.placeholder")}),
            "description": TextInput(
                attrs={"class": "form-control"},
            ),
            "icon": TextInput(
                attrs={"class": "form-control"},
            ),
            "url": URLInput(
                attrs={"class": "form-control", "placeholder": "https://"},
            ),
            "is_public": Select(
                attrs={"class": ""},
                choices={True: _("apps.manage.form.is_public.public"), False: _("apps.manage.form.is_public.private")},
            ),
            "is_pinned": Select(
                attrs={"class": ""},
                choices={True: _("apps.manage.form.is_pinned.yes"), False: _("apps.manage.form.is_pinned.no")},
            ),
        }
        labels = {
            "name": _("apps.manager.form.name.label"),
            "description": _("apps.manager.form.description.label"),
            "url": _("apps.manager.form.url.label"),
            "icon": _("apps.manager.form.icon.label"),
            "is_public": _("apps.manager.form.is_public.label"),
            "is_pinned": _("apps.manager.form.is_pinned.label"),
        }
        help_texts = {
            "icon": _("apps.manager.form.icon.help_text %(url)s") % {"url": "https://pictogrammers.com/library/mdi/"},
            "description": _("apps.manager.form.description.help_text"),
            "is_public": _("apps.manager.form.is_public.help_text"),
            "is_pinned": _("apps.manager.form.is_pinned.help_text"),
        }
