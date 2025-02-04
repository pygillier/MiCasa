from django.forms.widgets import TextInput


class IconInput(TextInput):
    template_name = "widgets/icon_input.html"

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs)
        self.attrs.update(
            {
                "class": "icon-input",
                "x-model.fill": "icon",
            }
        )
