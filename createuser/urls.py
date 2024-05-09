from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name = "home"),
    path("register/", views.register, name = "register"),
    path("welcome/", views.welcome, name = "welcome"),
    path("publish/", views.publish, name = "publish"),
    path("login/", views.site_login, name = "mylogin"),
    path("logout/", views.site_logout, name = "mylogout"),
    path("detalle/", views.detalle_publicacion, name = "detalle_publicacion"),
    path("staffregister/",views.staffregister, name = "staffregister"),
]