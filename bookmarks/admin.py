from django.contrib import admin
from .models import BookmarkCategory, Bookmark


@admin.register(BookmarkCategory)
class BookmarkCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_public", "position")

    actions = ["make_public", "make_private"]

    @admin.action(description="Set public")
    def make_public(self, request, queryset):
        queryset.update(is_public=True)

    @admin.action(description="Set private")
    def make_private(self, request, queryset):
        queryset.update(is_public=False)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_public", "position")

    list_filter = ["category", "is_public"]

    actions = ["make_public", "make_private"]

    @admin.action(description="Set public")
    def make_public(self, request, queryset):
        queryset.update(is_public=True)

    @admin.action(description="Set private")
    def make_private(self, request, queryset):
        queryset.update(is_public=False)
