from django.shortcuts import render, redirect
from .models import Usuario, Publicacion, Oferta, Intercambio
from datetime import date
from dateutil.relativedelta import relativedelta
from .forms import UsuarioForm, PublicacionForm, LoginForm, StaffForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.
def home(request):
    return redirect('welcome')

def register(request):
    if (request.method == "POST"):
        context = {"forms" : UsuarioForm(request.POST)}
        correo_usuario = request.POST.get("correo").lower()
        not_bad_fields = True
        fecha_nacimiento = transformar_fecha(request.POST)
        if (not_bad_fields and not password_with_six_or_more_char(request.POST.get('password'))):
            not_bad_fields = set_error_mensaje(context, "La contraseña debe tener al menos 6 caracteres")
        if (not_bad_fields and is_correo_registered(correo_usuario)):
            not_bad_fields = set_error_mensaje(context, "El correo ya se encuentra registrado")
        if (not_bad_fields and is_dni_registered(request.POST.get("dni"))):
            not_bad_fields = set_error_mensaje(context, "El dni ya se encuentra registrado")
        if (not_bad_fields and not is_adult(fecha_nacimiento)):
            not_bad_fields = set_error_mensaje(context, "Se debe ser mayor de 18 años para registrarse")
        if(not not_bad_fields):
            return render(request, "registration/register.html", context)
        else:
            context = {"forms" : UsuarioForm()}
            extra_fields = {}
            extra_fields["nombre"] = request.POST.get("nombre")
            extra_fields["apellido"] = request.POST.get("apellido")
            extra_fields["dni"] = request.POST.get("dni")
            extra_fields["nacimiento"] = fecha_nacimiento
            Usuario.objects.create_user(correo_usuario,
                                        request.POST.get("password"),
                                         **extra_fields)
            context['mensaje'] = "El registro fue exitoso"
            return render(request, "registration/register.html", context)
    else:
        context = {"forms" : UsuarioForm()}
        # send_mail("Hola", "Buenas :)", "settings.EMAIL_HOST_USER", ["mateoalmaraz2000@gmail.com"])
        return render(request, "registration/register.html", context)

def staffregister(request):
    if request.method == "POST":
        context = {"forms" : StaffForm(request.POST)}
        correo_ayudante = request.POST.get("correo").lower()
        not_bad_fields = True
        if (not_bad_fields and is_correo_registered(correo_ayudante)):
            not_bad_fields = set_error_mensaje(context, "El correo ya se encuentra registrado")
        if (not_bad_fields and not password_with_six_or_more_char(request.POST.get('password'))):
            not_bad_fields = set_error_mensaje(context, "La contraseña debe tener al menos 6 caracteres")
        if(not not_bad_fields):
            return render(request, "registration/staffregister.html", context)
        else:
            context = {"forms" : StaffForm()}
            extra_fields = {}
            extra_fields["nombre"] = request.POST.get("nombre")
            extra_fields["apellido"] = request.POST.get("apellido")
            extra_fields["nacimiento"] = "1990-01-01"
            Usuario.objects.create_staff(correo_ayudante,
                                        request.POST.get("password"),
                                         **extra_fields)
            context['mensaje'] = "El registro fue exitoso"
            return render(request, "registration/staffregister.html", context)
    else:
        context = {"forms" : StaffForm()}
        return render(request, "registration/staffregister.html", context)       

def userlist(request):
    datos=Usuario.objects.filter(is_staff = 0,is_superuser = 0)
    if(request.method == "POST"):
        ayudante=Usuario.objects.filter(correo = request.POST.get("usuario"))
        ayudante.update(is_staff=True)
        return render(request, "userlist.html",{"datos":datos})
    else:
        return render(request, "userlist.html",{"datos":datos})



def site_login(request):
    context = {"forms" : LoginForm(), "mensaje" : ""}
    if request.method == "POST":
        username = request.POST["correo"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("welcome")
        else:
            context["mensaje"] = "Los datos ingresados son incorrectos"
            return render(request, "registration/login.html", context)
    else:
        return render(request, "registration/login.html", context)

def site_logout(request):
    logout(request)
    return redirect("mylogin")

@login_required(redirect_field_name=None)
def welcome(request):
    q = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    resultados = Publicacion.objects.all().exclude(id_usuario=request.user.id)
    if q:
        resultados = resultados.filter(titulo__icontains=q)
    if tipo:  # Si se ha seleccionado un tipo
        if tipo != 'Todos': # Si se seleccionó un tipo específico distinto de 'todos'
            resultados = resultados.filter(categoria=tipo.capitalize())
        # No aplicar filtro si se seleccionó 'todos'
    return render(request, 'welcome.html', {'resultados': resultados})

@login_required(redirect_field_name=None)
def publish(request):
    context = {"forms" : PublicacionForm()}
    if (request.method == "POST"):
        not_bad_fields = True
        publicacion_titulo = request.POST.get('titulo').capitalize()
        if (not_bad_fields and same_post_title(publicacion_titulo, request.user.id)):
            not_bad_fields = set_error_mensaje(context, "La publicacion tiene titulo repetido")
        if(not not_bad_fields):
            return render(request, "publish.html", context)
        else:
            publicacion = Publicacion(titulo = publicacion_titulo,
                            foto = request.POST.get("foto"),
                            descripcion = request.POST.get("descripcion"),
                            categoria = request.POST.get("categoria"),
                            id_usuario = request.user.id
                            )
            publicacion.save()
            return redirect("welcome")
    else:
        return render(request, "publish.html", context)

def detalle_publicacion(request,pk):
    item = Publicacion.objects.filter(id=pk)  # , id_usuario=request.user.id
    # print(request.user.id)
    data = {
        'item':item[0]
    }
    return render(request, 'detalle.html',data)

def borrar(request,pk):
    item = Publicacion.objects.get(id=pk)
    if(item.id_usuario == request.user.id or request.user.is_staff or request.user.is_superuser):
        item.delete()
    return redirect('welcome')

def ver_publicaciones(request):
    mis_publicaciones=Publicacion.objects.filter(id_usuario=request.user.id)
    data = {
        'item':mis_publicaciones
    }
    return render(request, 'ver_publicaciones.html', data)

def cancelar_intercambio(request, context):
    intercambio = Intercambio.objects.filter(codigo_intercambio=context["codigo"])
    intercambio.update(estado=context["estado"])
    intercambio.update(motivo_cancelacion=context["motivo_cancelacion"]) 
    send_mail(
        context["codigo"] + "Intercambio cancelado",
        "El intercambio con codigo: " + context["codigo"] + "a sido cancelado por: " + context["motivo_cancelacion"], 
        "settings.EMAIL_HOST_USER", 
        context["emails"])
    return redirect('welcome')

def guardar_oferta(request):
    if request.method == 'POST':
        # Procesar la oferta recibida del formulario
        tit = request.POST.get('titulo')
        cant = request.POST.get('cantidad')
        desc = request.POST.get('descripcion')
        Oferta.objects.create(id_publicacion = id, titulo = tit, cantidad = cant, descripcion = desc)
        # Lógica para guardar la oferta en la base de datos, por ejemplo:
        # oferta = Oferta(monto=monto_oferta, usuario=request.user)
        # oferta.save()
        # Redirigir a una página de éxito o a la página de la publicación
        return redirect("welcome")
    else:
        # Si se accede a la URL directamente, redirigir a alguna página
        return redirect("welcome")
    



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

def set_error_mensaje(context, mensaje):
    context['mensaje'] = mensaje
    return False

def same_post_title(pedido, id_usuario_actual):
    return Publicacion.objects.filter(titulo=pedido, id_usuario=id_usuario_actual).exists()
