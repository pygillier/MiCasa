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
    path("category/reorder/", views.ReorderCategoryView.as_view(), name="category_reorder"),
    path("bookmark/create/", views.BookmarkCreateView.as_view(), name="bookmark_create"),
    path("bookmark/<int:pk>/update/", views.BookmarkUpdateView.as_view(), name="bookmark_update"),
    path("bookmark/<int:pk>/delete/", views.BookmarkDeleteView.as_view(), name="bookmark_delete"),
    path("bookmarks/reorder/", views.BookmarkReorderView.as_view(), name="bookmark_reorder"),
]
