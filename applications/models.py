from django.db import models
from urllib.parse import urlparse


class Application(models.Model):
    name = models.CharField(max_length=250, unique=True, null=False)
    url = models.URLField(unique=True, null=False)
    description = models.CharField(max_length=250, blank=True)
    is_public = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, null=True, blank=True)
    position = models.IntegerField(unique=False, null=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]

    @property
    def subtitle(self):
        if self.description:
            return self.description
        else:
            # Remove scheme from url
            o = urlparse(self.url)
            return o.hostname

    def clean(self):
        # Update default position
        if self.position == 0:
            try:
                latest = Application.objects.latest("position")
                self.position = latest.position + 1
            except Application.DoesNotExist:
                self.position = 1

    def __str__(self):
        return self.name

    def export(self) -> dict:
        """
        Export a portable version of application details as a dictionary for backup.
        :return: dict
        """
        return {
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "is_public": self.is_public,
            "is_pinned": self.is_pinned,
            "icon": self.icon,
            "position": self.position,
        }
