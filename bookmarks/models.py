from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models


class BookmarkCategory(models.Model):
    name = models.CharField(max_length=250, unique=True, null=False)
    is_public = models.BooleanField(default=False)
    position = models.IntegerField(null=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        verbose_name = "Category"
        ordering = ["position"]

    def clean(self):
        # Update default position
        if self.position == 0:
            try:
                latest = BookmarkCategory.objects.latest("position")
                self.position = latest.position + 1
            except BookmarkCategory.DoesNotExist:
                self.position = 1

    def __str__(self):
        return self.name

    def export(self) -> dict:
        return {
            "name": self.name,
            "is_public": self.is_public,
            "position": self.position,
            "bookmarks": [bookmark.export() for bookmark in self.bookmark_set.all()],
        }


class Bookmark(models.Model):
    name = models.CharField(max_length=250, unique=False, null=False)
    url = models.URLField(unique=True, null=False)
    category = models.ForeignKey(BookmarkCategory, on_delete=models.CASCADE, null=False, related_name="bookmarks")
    icon = models.CharField(max_length=50, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    position = models.IntegerField(unique=False, null=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]

    def clean(self):
        # A bookmark can't be public if the related category is not public
        if self.is_public is True and self.category.is_public is False:
            raise ValidationError({"is_public": _("A bookmark can't be public if the category is private.")})
        # Update default position
        if self.position == 0:
            try:
                latest = Bookmark.objects.filter(category=self.category).latest("position")
                self.position = latest.position + 1
            except Bookmark.DoesNotExist:
                self.position = 1

    def __str__(self):
        return self.name

    def export(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "icon": self.icon,
            "is_public": self.is_public,
            "position": self.position,
        }

    def public_icon(self):
        return self.icon if self.icon else "bookmark"
