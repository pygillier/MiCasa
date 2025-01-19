from django.forms import ModelForm, Select, TextInput, URLInput
from .models import Application
from django.utils.translation import gettext_lazy as _


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ["name", "description", "url", "icon", "is_public", "is_pinned"]
        widgets = {
            "name": TextInput(attrs={"id": "app_name", "placeholder": _("forms.apps.name_placeholder")}),
            "url": URLInput(attrs={"placeholder": _("forms.url_placeholder")}),
            "is_public": Select(
                choices={True: _("forms.is_public.public_field"), False: _("forms.is_public.private_field")}
            ),
            "is_pinned": Select(
                choices={True: _("apps.manage.form.is_pinned.yes"), False: _("apps.manage.form.is_pinned.no")}
            ),
        }
        labels = {
            "name": _("forms.name_label"),
            "description": _("forms.apps.description_label"),
            "url": _("forms.url_label"),
            "icon": _("forms.icon_label"),
            "is_public": _("forms.is_public_label"),
            "is_pinned": _("forms.is_pinned_label"),
        }
        help_texts = {
            "icon": _("forms.icon_help_text %(url)s") % {"url": "https://pictogrammers.com/library/mdi/"},
            "description": _("forms.apps.description_help_text"),
            "is_public": _("forms.is_public_help_text"),
            "is_pinned": _("forms.is_pinned_help_text"),
        }
