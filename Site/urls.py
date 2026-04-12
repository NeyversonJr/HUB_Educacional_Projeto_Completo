from django.urls import path

from . import views

app_name = "Site"

urlpatterns = [
    path("", views.index, name="index"),
]
