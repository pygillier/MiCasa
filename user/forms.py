from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms


class SetupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()


class DataImportForm(forms.Form):
    source = forms.FileField()
