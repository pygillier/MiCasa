from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("setup/", views.SetupView.as_view(), name="setup"),
    path("language/", views.LanguageSelectorView.as_view(), name="language"),
    path("about/", views.AboutView.as_view(), name="about"),
]
