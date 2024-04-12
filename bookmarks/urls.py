from django.urls import path

from . import views

app_name = "bookmarks"

urlpatterns = [
    # path("", views.IndexView.as_view(), name="index"),
    path("home/", views.HomeView.as_view(), name="home"),
]
