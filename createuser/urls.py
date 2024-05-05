from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name = "register"),
    path("welcome/", views.welcome, name = "welcome"),
    path("publish/", views.publish, name = "publish"),
]