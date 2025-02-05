from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

app_name = "user"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("setup/", views.SetupView.as_view(), name="setup"),
    path("weather/", views.WeatherView.as_view(), name="weather"),
    path("theme/", views.ThemeView.as_view(), name="theme"),
    path("backup/", views.BackupView.as_view(), name="backup"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
