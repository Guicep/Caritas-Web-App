from django.shortcuts import render, redirect
from .models import Usuario, Publicacion
from datetime import date
from dateutil.relativedelta import relativedelta
from .forms import UsuarioForm, PublicacionForm, LoginForm, StaffForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def home(request):
    return redirect('welcome')

def register(request):
    context = {"forms" : UsuarioForm()}
    if (request.method == "POST"):
        not_bad_fields = True
        fecha_nacimiento = transformar_fecha(request.POST)
        if (not_bad_fields and not password_with_six_or_more_char(request.POST.get('password'))):
            not_bad_fields = set_context_error_mensaje(context, "La contraseña debe tener al menos 6 caracteres")
        if (not_bad_fields and is_correo_registered(request.POST.get("correo"))):
            not_bad_fields = set_context_error_mensaje(context, "El correo ya se encuentra registrado")
        if (not_bad_fields and is_dni_registered(request.POST.get("dni"))):
            not_bad_fields = set_context_error_mensaje(context, "El dni ya se encuentra registrado")
        if (not_bad_fields and not is_adult(fecha_nacimiento)):
            not_bad_fields = set_context_error_mensaje(context, "Se debe ser mayor de 18 años para registrarse")

        if(not not_bad_fields):
            return render(request, "registration/register.html", context)
        else:
            extra_fields = {}
            extra_fields["nombre"] = request.POST.get("nombre")
            extra_fields["apellido"] = request.POST.get("apellido")
            extra_fields["dni"] = request.POST.get("dni")
            extra_fields["nacimiento"] = fecha_nacimiento
            Usuario.objects.create_user(request.POST.get("correo"),
                                         request.POST.get("password"),
                                         **extra_fields)
            context['mensaje'] = "El registro fue exitoso"
            return render(request, "registration/register.html", context)
    else:
        return render(request, "registration/register.html", context)

def staffregister(request):
    context = {"forms" : StaffForm()}
    if request.method == "POST":
        not_bad_fields = True
        if (not_bad_fields and is_correo_registered(request.POST.get("correo"))):
            not_bad_fields = set_context_error_mensaje(context, "El correo ya se encuentra registrado")
        if (not_bad_fields and not password_with_six_or_more_char(request.POST.get('password'))):
            not_bad_fields = set_context_error_mensaje(context, "La contraseña debe tener al menos 6 caracteres")
        if(not not_bad_fields):
            return render(request, "registration/staffregister.html", context)
        else:
            extra_fields = {}
            extra_fields["nombre"] = request.POST.get("nombre")
            extra_fields["apellido"] = request.POST.get("apellido")
            extra_fields["nacimiento"] = "1990-01-01"
            Usuario.objects.create_staff(request.POST.get("correo"),
                                         request.POST.get("password"),
                                        
                                         **extra_fields)
            context['mensaje'] = "El registro fue exitoso"
            return render(request, "registration/staffregister.html", context)
    else:
        return render(request, "registration/staffregister.html", context)        




def site_login(request):
    context = {"forms" : LoginForm(), "mensaje" : ""}
    if request.method == "POST":
        username = request.POST["correo"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, "welcome.html")
        else:
            context["mensaje"] = "El mail o la contraseña son erroneos"
            return render(request, "registration/login.html", context)
    else:
        return render(request, "registration/login.html", context)

def site_logout(request):
    logout(request)
    return redirect("mylogin")

@login_required
def welcome(request):
    datos = Publicacion.objects.all()
    data = {
        'datos': datos
    }
    return render(request, 'welcome.html', data)

@login_required
def publish(request):
    context = {"forms" : PublicacionForm()}
    if (request.method == "POST"):
        not_bad_fields = True
        if (not_bad_fields and same_post_title(request.POST.get('titulo'), request.user.id)):
            not_bad_fields = set_context_error_mensaje(context, "La publicacion tiene titulo repetido")

        if(not not_bad_fields):
            return render(request, "publish.html", context)
        else:
            publicacion = Publicacion(titulo = request.POST.get("titulo"),
                              foto = request.POST.get("foto"),
                              descripcion = request.POST.get("descripcion"),
                              id_usuario = request.user.id
                              )
            publicacion.save()
            return redirect("welcome")
    else:
        return render(request, "publish.html", context)

def detalle_publicacion(request):
    item = Publicacion.objects.filter(id=1)  # , id_usuario=request.user.id
    # print(request.user.id)
    data = {
        'item':item[0]
    }
    return render(request, 'detalle.html',data)

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