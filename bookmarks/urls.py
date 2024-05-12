from django.urls import path

from . import views

app_name = "bookmarks"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("manage/", views.ManageView.as_view(), name="manage"),
    path("category/create/", views.CategoryCreateView.as_view(), name="category_create"),
    path("category/<int:pk>/update/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("category/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
]
