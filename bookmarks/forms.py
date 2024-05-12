from django.forms import ModelForm, TextInput, Select
from .models import BookmarkCategory
from django.utils.translation import gettext_lazy as _


class BookmarkCategoryForm(ModelForm):
    class Meta:
        model = BookmarkCategory
        fields = ["name", "is_public"]
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": _("bm.category.form.name.placeholder")}),
            "description": TextInput(
                attrs={"class": "form-control"},
            ),
            "is_public": Select(
                attrs={"class": "form-select"},
                choices={
                    True: _("bm.category.form.is_public.public.text"),
                    False: _("bm.category.form.is_public.private.text"),
                },
            ),
        }
        labels = {
            "name": _("bm.category.form.name.label"),
            "is_public": _("bm.category.form.is_public.label"),
        }
        help_texts = {
            "is_public": _("bm.category.form.is_public.help_text"),
        }
