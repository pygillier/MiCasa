from django.views.generic import ListView, TemplateView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from . import models, forms
from django.urls import reverse_lazy
from django.utils.translation import gettext as _


class ManageBookmarksMixin(ContextMixin):
    extra_context = {"current": "bookmarks"}


class IndexView(ListView):
    model = models.BookmarkCategory
    template_name = "bookmarks/index.html"
    context_object_name = "categories"

    def get_queryset(self):
        qs = super().get_queryset()

        # Anonymous
        if self.request.user.is_anonymous:
            qs = qs.filter(is_public=True)

        return qs


class HomeView(ListView):
    model = models.BookmarkCategory
    template_name = "bookmarks/home.html"
    context_object_name = "categories"

    def get_queryset(self):
        qs = super().get_queryset()

        # Anonymous
        if self.request.user.is_anonymous:
            qs = qs.filter(is_public=True)

        return qs


class ManageView(LoginRequiredMixin, ManageBookmarksMixin, TemplateView):
    template_name = "bookmarks/manage.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()

        # Fetch all categories & bookmarks
        ctx["categories"] = models.BookmarkCategory.objects.all()
        ctx["bookmarks"] = models.Bookmark.objects.all()

        return ctx


# Category management
class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, ManageBookmarksMixin, CreateView):
    model = models.BookmarkCategory
    template_name = "bookmarks/category/create.html"
    form_class = forms.BookmarkCategoryForm

    success_url = reverse_lazy("bookmarks:manage")
    success_message = _("bm.category.create.success %(name)s")

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, ManageBookmarksMixin, UpdateView):
    model = models.BookmarkCategory
    template_name = "bookmarks/category/update.html"
    form_class = forms.BookmarkCategoryForm

    success_url = reverse_lazy("bookmarks:manage")
    success_message = _("bm.category.update.success %(name)s")

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


class CategoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, ManageBookmarksMixin, DeleteView):
    template_name = "bookmarks/category/delete.html"
    context_object_name = "category"
    model = models.BookmarkCategory

    success_url = reverse_lazy("bookmarks:manage")
    success_message = _("bm.category.delete.success %(name)s")

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


# Bookmarks management
class BookmarkCreateView(LoginRequiredMixin, SuccessMessageMixin, ManageBookmarksMixin, CreateView):
    model = models.Bookmark
    template_name = "bookmarks/bookmark/create.html"
    form_class = forms.BookmarkForm

    success_url = reverse_lazy("bookmarks:manage")
    success_message = _("bm.bookmark.create.success %(name)s")

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


class BookmarkUpdateView(LoginRequiredMixin, SuccessMessageMixin, ManageBookmarksMixin, UpdateView):
    model = models.Bookmark
    template_name = "bookmarks/bookmark/update.html"
    form_class = forms.BookmarkForm

    success_url = reverse_lazy("bookmarks:manage")
    success_message = _("bm.bookmark.update.success %(name)s")

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


class BookmarkDeleteView(LoginRequiredMixin, SuccessMessageMixin, ManageBookmarksMixin, DeleteView):
    template_name = "bookmarks/bookmark/delete.html"
    context_object_name = "bookmark"
    model = models.Bookmark

    success_url = reverse_lazy("bookmarks:manage")
    success_message = _("bm.bookmark.delete.success %(name)s")

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )
