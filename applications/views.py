from django.views.generic import ListView
from .models import Application


class HomeView(ListView):
    model = Application
    template_name = "applications/home.html"
    context_object_name = "applications"

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_anonymous:
            return qs.filter(is_public=True)
        else:
            return qs
