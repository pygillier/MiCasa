from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_public", "position")

    actions = ["make_public", "make_private"]

    @admin.action(description="Set public")
    def make_public(self, request, queryset):
        queryset.update(is_public=True)

    @admin.action(description="Set private")
    def make_private(self, request, queryset):
        queryset.update(is_public=False)
