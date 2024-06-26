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
    path('historial/', views.ver_historial, name='historial'),
    path('cancelar_intercambio/<int:id>', views.cancelar_intercambio, name='cancelar_intercambio'),
    path('listar_intercambios', views.listar_intercambios, name='listar_intercambios'),
    path('confirmar_intercambio/<int:id>', views.confirmar_intercambio, name='confirmar_intercambio'),
    path('comentario/editar/<int:comentario_id>/', views.editar_comentario, name='editar_comentario'),
    path('eliminar_comentario/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),
    path('listar_donaciones/', views.listar_donaciones, name='listar_donaciones'),
    path('registrar_tarjeta/', views.registrar_tarjeta, name='registrar_tarjeta'),
    path('registrar_producto/', views.registrar_producto, name='registrar_producto'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
]