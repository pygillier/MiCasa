from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("manage/", views.ManageListView.as_view(), name="manage"),
    path("create/", views.CreateApplicationView.as_view(), name="create"),
    path("<int:pk>/update/", views.UpdateApplicationView.as_view(), name="update"),
    path("<int:pk>/delete/", views.DeleteApplicationView.as_view(), name="delete"),
]
