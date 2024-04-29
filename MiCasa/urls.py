from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("bookmarks/", include("bookmarks.urls")),
    path("applications/", include("applications.urls")),
    path("manage/", include("user.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("__debug__/", include("debug_toolbar.urls")),
]
