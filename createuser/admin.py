from django.contrib import admin
from .models import Usuario, Publicacion, Oferta, Intercambio, Comentario, DonacionProducto, DonacionEfectivo, CodigosRecuperacion


# Register your models here.

admin.site.register(Usuario)
admin.site.register(Publicacion)
admin.site.register(Oferta)
admin.site.register(Intercambio)
admin.site.register(Comentario)
admin.site.register(DonacionProducto)
admin.site.register(DonacionEfectivo)
admin.site.register(CodigosRecuperacion)

