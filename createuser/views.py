from django.shortcuts import render, redirect
from .models import Usuario, Publicacion
from datetime import date
from dateutil.relativedelta import relativedelta
from .forms import UsuarioForm, PublicacionForm

# Create your views here.
def register(request):
    context = {"forms" : UsuarioForm()}
    if (request.method == "POST"):
        not_bad_fields = True
        fecha_nacimiento = transformar_fecha(request.POST)
        if (not_bad_fields and not password_with_six_or_more_char(request.POST.get('password'))):
            not_bad_fields = set_context_error_mensaje(context, "La contraseña debe tener al menos 6 caracteres")
        if (not_bad_fields and is_correo_registered(request.POST.get("correo"))):
            not_bad_fields = set_context_error_mensaje(context, "El correo se encuentra registrado")
        if (not_bad_fields and is_dni_registered(request.POST.get("dni"))):
            not_bad_fields = set_context_error_mensaje(context, "El dni se encuentra registrado")
        if (not_bad_fields and not is_adult(fecha_nacimiento)):
            not_bad_fields = set_context_error_mensaje(context, "Debe de tener 18 años o mas")

        if(not not_bad_fields):
            return render(request, "register.html", context)
        else:
            usuario = Usuario(nombre = request.POST.get("nombre"),
                              apellido = request.POST.get("apellido"),
                              dni = request.POST.get("dni"),
                              correo = request.POST.get("correo"),
                              password = request.POST.get("password"),
                              nacimiento = fecha_nacimiento,
                              )
            usuario.save()
            context['mensaje'] = "El registro fue exitoso"
            return render(request, "register.html", context)
    else:
        return render(request, "register.html", context)

def welcome(request):
    return render(request, "welcome.html")

def publish(request):
    context = {"forms" : PublicacionForm()}
    if (request.method == "POST"):
        not_bad_fields = True
        id_usuario_actual = 1 # Hace referencia al usuario logueado y a quien asocia la publicacion
        if (not_bad_fields and same_post_title(request.POST.get('titulo'), id_usuario_actual)):
            not_bad_fields = set_context_error_mensaje(context, "La publicacion tiene titulo repetido")

        if(not not_bad_fields):
            return render(request, "publish.html", context)
        else:
            publicacion = Publicacion(titulo = request.POST.get("titulo"),
                              foto = request.POST.get("foto"),
                              descripcion = request.POST.get("descripcion"),
                              id_usuario = 1
                              )
            publicacion.save()
            return redirect("http://127.0.0.1:8000/welcome/")
    else:
        return render(request, "publish.html", context)

# Funciones de validacion y transformacion
def password_with_six_or_more_char(cadena):
    return len(cadena) >= 6

def is_correo_registered(pedido):
    return Usuario.objects.filter(correo=pedido).exists()

def is_dni_registered(pedido):
    return Usuario.objects.filter(dni=pedido).exists()

def is_adult(fecha):
    return not (relativedelta(date.today(), fecha).years) < 18

def transformar_fecha(pedido):
    return date(int(pedido.get("anio")), int(pedido.get("mes")), int(pedido.get("dia")))

def set_context_error_mensaje(context, mensaje):
    context['mensaje'] = mensaje
    return False

def same_post_title(pedido, id_usuario_actual):
    return Publicacion.objects.filter(titulo=pedido, id_usuario=id_usuario_actual).exists()