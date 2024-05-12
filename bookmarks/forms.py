from django.forms import ModelForm, TextInput, Select, URLInput
from .models import BookmarkCategory, Bookmark
from django.utils.translation import gettext_lazy as _


class BookmarkCategoryForm(ModelForm):
    class Meta:
        model = BookmarkCategory
        fields = ["name", "is_public"]
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": _("bm.category.form.name.placeholder")}),
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


class BookmarkForm(ModelForm):
    class Meta:
        model = Bookmark
        fields = ["name", "url", "category", "is_public"]
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": _("bm.bookmark.form.name.placeholder")}),
            "url": URLInput(attrs={"class": "form-control", "placeholder": _("bm.bookmark.form.url.placeholder")}),
            "category": Select(
                attrs={"class": "form-select"},
            ),
            "is_public": Select(
                attrs={"class": "form-select"},
                choices={
                    True: _("bm.bookmark.form.is_public.public.text"),
                    False: _("bm.bookmark.form.is_public.private.text"),
                },
            ),
        }
        labels = {
            "name": _("bm.bookmark.form.name.label"),
            "url": _("bm.bookmark.form.url.label"),
            "category": _("bm.bookmark.form.category.label"),
            "is_public": _("bm.bookmark.form.is_public.label"),
        }
        help_texts = {
            "is_public": _("bm.bookmark.form.is_public.help_text"),
        }
