from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name = "home"),
    path("register/", views.register, name = "register"),
    path("welcome/", views.welcome, name = "welcome"),
    path("publish/", views.publish, name = "publish"),
    path("login/", views.site_login, name = "mylogin"),
    path("logout/", views.site_logout, name = "mylogout"),
    path("detalle/<int:pk>", views.detalle_publicacion, name = "detalle_publicacion"),
    path("staffregister/",views.staffregister, name = "staffregister"),
    path("borrar/<int:pk>", views.borrar, name = "borrar"),
    path("verpublicaciones/", views.ver_publicaciones, name = "ver_publicaciones"),
    path("userlist/",views.userlist, name= "userlist"),
    path("guardar-oferta/", views.guardar_oferta, name="guardar_oferta"),
    path("ofertas/<int:pk>", views.ofertas, name="ofertas"),
    path("detalle_oferta/<int:pk>", views.detalle_oferta, name="detalle_oferta"),
    path('oferta_aceptada/', views.oferta_aceptada, name='oferta_aceptada'),
    path('oferta_rechazada/', views.oferta_rechazada, name='oferta_rechazada'),
]