from django.contrib import admin
from .models import Usuario, Publicacion, Oferta, Intercambio, Comentario

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Publicacion)
admin.site.register(Oferta)
admin.site.register(Intercambio)
admin.site.register(Comentario)

