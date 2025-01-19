from django.forms import ModelForm, TextInput, Select, URLInput
from .models import BookmarkCategory, Bookmark
from django.utils.translation import gettext_lazy as _


class BookmarkCategoryForm(ModelForm):
    class Meta:
        model = BookmarkCategory
        fields = ["name", "is_public"]
        widgets = {
            "name": TextInput(attrs={"placeholder": _("forms.categories.name_placeholder")}),
            "is_public": Select(
                choices={
                    True: _("forms.is_public.public_field"),
                    False: _("forms.is_public.private_field"),
                }
            ),
        }
        labels = {
            "name": _("forms.name_label"),
            "is_public": _("forms.is_public_label"),
        }
        help_texts = {
            "is_public": _("forms.is_public_help_text"),
        }


class BookmarkForm(ModelForm):
    class Meta:
        model = Bookmark
        fields = ["name", "url", "category", "is_public"]
        widgets = {
            "name": TextInput(attrs={"placeholder": _("forms.bookmarks.name_placeholder")}),
            "url": URLInput(attrs={"placeholder": _("forms.url_placeholder")}),
            "is_public": Select(
                choices={
                    True: _("forms.is_public.public_field"),
                    False: _("forms.is_public.private_field"),
                }
            ),
        }
        labels = {
            "name": _("forms.name_label"),
            "url": _("forms.url_label"),
            "category": _("forms.bookmarks.category_label"),
            "is_public": _("forms.is_public_label"),
        }
        help_texts = {
            "is_public": _("forms.is_public_help_text"),
        }
