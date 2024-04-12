from django.views.generic import ListView
from .models import BookmarkCategory


class HomeView(ListView):
    model = BookmarkCategory
    template_name = "bookmarks/home.html"
    context_object_name = "categories"

    def get_queryset(self):
        qs = super().get_queryset()

        # Anonymous
        if self.request.user.is_anonymous:
            qs = qs.filter(is_public=True)

        return qs
