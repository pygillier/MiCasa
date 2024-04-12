from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("bookmarks/", include("bookmarks.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
