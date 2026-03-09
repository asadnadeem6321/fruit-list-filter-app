from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("fruit", views.fruit_api, name="fruit_api"),
]
