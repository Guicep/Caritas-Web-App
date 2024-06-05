from django.shortcuts import render, redirect
from .models import Usuario, Publicacion, Oferta, Intercambio, Comentario
from datetime import date
from dateutil.relativedelta import relativedelta
from .forms import UsuarioForm, PublicacionForm, LoginForm, StaffForm, ComentarioForm, IntercambioForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import os
from itertools import chain, zip_longest
from django.shortcuts import render, get_object_or_404

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
    ofertas_usuario = Oferta.objects.filter(id_ofertante=request.user.id).values_list("pk", flat=True)
    resultados_ocultos_ofertante = Intercambio.objects.filter(id_ofertante__in=ofertas_usuario).values_list("id_publicacion", flat=True)
    resultados_publicacion_ocultas = Publicacion.objects.filter(pk__in=resultados_ocultos_ofertante)
    resultados = Publicacion.objects.all().exclude(id_usuario=request.user.id).exclude(oculto=True) | resultados_publicacion_ocultas
    print(resultados)

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
                            id_usuario = request.user.id,
                            oculto = False,
                            )
            publicacion.save()
            return redirect("welcome")
    else:
        return render(request, "publish.html", context)

def detalle_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, id=pk)
    comentarios = Comentario.objects.filter(publicacion=publicacion, respuesta__isnull=True)
    usuarios_ofertantes = Oferta.objects.filter(id_publicacion=pk).values_list('id_ofertante', flat=True)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.publicacion = publicacion
            comentario.usuario = request.user
            if 'respuesta' in request.POST:
                comentario.respuesta_id = request.POST.get('comentario_id')
                comentario.save()
                comentario_respondido = Comentario.objects.get(id=comentario.respuesta_id)
                comentario_respondido.respondido = True
                comentario_respondido.save()
            else:
                comentario.save()
            return redirect('detalle_publicacion', pk=pk)
    else:
        form = ComentarioForm()

    respuesta_form = ComentarioForm()

    data = {
        'item': publicacion,
        'comentarios': comentarios,
        'form': form,
        'respuesta_form': respuesta_form,
        'tiene_oferta' : request.user.id in usuarios_ofertantes,
    }
    return render(request, 'detalle.html', data)

def detalle_oferta(request,pk):
    oferta = get_object_or_404(Oferta, id=pk)
    data = {
        'item': oferta
    }
    return render(request, 'detalle_oferta.html', data)


def borrar(request,pk):
    item = Publicacion.objects.get(id=pk)
    user = Usuario.objects.get(id=item.id_usuario)
    if(item.id_usuario == request.user.id or request.user.is_staff or request.user.is_superuser):
        send_mail(
            "Publicacion Eliminada",
            "Tu Publicacion: "+item.titulo+" a sido eliminada",
            "settings.EMAIL_HOST_USER",
            [user.correo])
        item.delete()
    return redirect('ver_publicaciones')

def ver_publicaciones(request):
    mis_publicaciones=Publicacion.objects.filter(id_usuario=request.user.id)
    data = {
        'item':mis_publicaciones
    }
    return render(request, 'ver_publicaciones.html', data)

def ofertas(request,pk):
    mis_ofertas = Oferta.objects.filter(id_publicacion=pk)
    data = {
        'item': mis_ofertas
    }
    return render(request, 'ver_ofertas.html', data)

def guardar_oferta(request):
    if request.method == 'POST':
        # Procesar la oferta recibida del formulario
        id_pu = request.POST.get('id_publicacion')
        id_of = request.POST.get('id_ofertante')
        tit = request.POST.get('titulo')
        cant = request.POST.get('cantidad')
        desc = request.POST.get('descripcion')
        Oferta.objects.create(id_publicacion = id_pu, id_ofertante = id_of, titulo = tit, cantidad = cant, descripcion = desc, aceptada = False)
        # Lógica para guardar la oferta en la base de datos, por ejemplo:
        # oferta = Oferta(monto=monto_oferta, usuario=request.user)
        # oferta.save()
        # Redirigir a una página de éxito o a la página de la publicación
        return redirect("detalle_publicacion", pk=id_pu)
    else:
        # Si se accede a la URL directamente, redirigir a alguna página
        return redirect("welcome")
    

def oferta_aceptada(request):
    if request.method == 'POST':
        oferta = Oferta.objects.filter(id=request.POST.get('oferta_id'))
        publicacion = Publicacion.objects.filter(id=oferta.get().id_publicacion)
        publicante = Usuario.objects.filter(pk=publicacion.get().id_usuario)
        ofertante = Usuario.objects.filter(pk=oferta.get().id_ofertante)
        intercambio = Intercambio.objects.create(
            id_publicacion=publicacion.get().pk,
            id_ofertante=oferta.get().pk,
            estado="Pendiente",
            motivo_cancelacion="",
            )
        publicacion.update(oculto=True)
        oferta.update(aceptada=True)
        resultado = Intercambio.objects.filter(pk=intercambio.pk)
        resultado.update(codigo_intercambio=1000+intercambio.pk)
        #send_mail(
        #    "Aviso de oferta aceptada!",
        #    "La oferta "+oferta.get().titulo+" en la publicación "+publicacion.get().titulo+
        #    " de "+publicante.get().apellido+" "+publicante.get().nombre +" a sido aceptada!\n\n"+
        #    "Su intercambio se realizara el dia "+resultado.get().fecha_acordada.strftime('%d/%m/%Y')+" con el codigo: "+
        #    resultado.get().codigo_intercambio+" en la filial de La Plata",
        #    "settings.EMAIL_HOST_USER",
        #    [ofertante.get().correo],
        #)
    return redirect("detalle_publicacion", pk=publicacion.get().pk)

def oferta_rechazada(request):
    oferta = Oferta.objects.filter(pk=request.POST.get("oferta_id"))
    publicacion = Publicacion.objects.filter(pk=oferta.get().id_publicacion)
    publicante = Usuario.objects.filter(pk=publicacion.get().id_usuario)
    ofertante = Usuario.objects.filter(pk=oferta.get().id_ofertante)
    send_mail(
        "Aviso de oferta cancelada",
        "Su oferta "+oferta.get().titulo+" en la publicación "+publicacion.get().titulo+
        " de "+publicante.get().apellido+" "+publicante.get().nombre +" fue rechazada",
        "settings.EMAIL_HOST_USER",
        [ofertante.get().correo],
    )
    oferta.delete()
    return redirect('ver_publicaciones')

def cancelar_intercambio(request, id):
    intercambio = Intercambio.objects.filter(id_publicacion=id)
    intercambio.update(estado="Cancelado")
    intercambio.update(motivo_cancelacion=request.POST.get('motivo'))
    publicacion = Publicacion.objects.filter(pk=id)
    publicacion.update(oculto=False)
    oferta = Oferta.objects.filter(pk=intercambio.get().id_ofertante)
    oferta.delete()
    intercambio.update(id_ofertante=-1)
    #send_mail(
    #    context["codigo"] + "Intercambio cancelado",
    #    "El intercambio con codigo: " + context["codigo"] + "a sido cancelado por: " + context["motivo_cancelacion"], 
    #    "settings.EMAIL_HOST_USER", 
    #    context["emails"])
    return redirect('welcome')

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

#def ver_historial(request):
    #historial =Oferta.objects.filter(id_ofertante=request.user.id)
    #print(historial)#get().titulo
    #ofertas = Oferta.objects.filter(id_ofertante=request.user.id)
    #oferta_ids = ofertas.values_list('id', flat=True)
    #hola=Intercambio.objects.filter(id_ofertante__in=oferta_ids)
    #print(hola.get().id_publicacion)
    #return redirect("welcome")

def ver_historial(request):
    usuario_id = request.user.id

    id_ou = Oferta.objects.filter(id_ofertante=request.user.id).values_list('pk',flat=True)
    print(id_ou)
    # agaro ids de las ofertas enviadas por el usuario que han sido aceptadas 
    #ids_ofertas_enviadas_aceptadas = Intercambio.objects.filter(id_ofertante__in=Oferta.objects.filter(id_ofertante=request.user.id).values_list('id', flat=True)).values_list('id', flat=True)
    ids_ofertas_enviadas_aceptadas = Intercambio.objects.filter(id_ofertante__in=id_ou).values_list('pk',flat=True)
    ids_ofertas_inter = Intercambio.objects.filter(id_ofertante__in=id_ou).values_list('id_ofertante',flat=True)
    print(ids_ofertas_enviadas_aceptadas)
    # aca agarro todas las id de publicaciones de los intercambios
    ids_publicaciones_intercambios = Intercambio.objects.filter().values_list('id_publicacion', flat=True)
    #aca tengo que agarra de las publicaciones que tienen intercambio y me guardo el id del usuario
    publicaciones_que_intercambios = Publicacion.objects.filter(id__in=ids_publicaciones_intercambios)
    #aca tengo publicaciones del usuario que son intercambios, o sea hay que mostrar
    publicaciones_del_usuario_quesonintercambio = publicaciones_que_intercambios.filter(id_usuario=request.user.id).values_list('id', flat=True)
    #ofertas recibidas que se transformaron en intercambio, ya estoy loco en este punto.
    ofertas_recibidas= Oferta.objects.filter(id_publicacion__in=publicaciones_del_usuario_quesonintercambio).values_list('id', flat=True)

    intercambios1= Intercambio.objects.filter(id_ofertante__in=ofertas_recibidas)
    idsp = Intercambio.objects.filter(id_ofertante__in=ofertas_recibidas).values_list('id_publicacion',flat=True)
    idso = Intercambio.objects.filter(id_ofertante__in=ofertas_recibidas).values_list('id_ofertante',flat=True)
    nombre_mis = Publicacion.objects.filter(id__in=idsp).values_list('titulo',flat=True)
    o = Oferta.objects.filter(id__in=idso).values_list('titulo', flat=True)


    intercambios2= Intercambio.objects.filter(id__in=ids_ofertas_enviadas_aceptadas)

    nom_oe = Oferta.objects.filter(id__in=ids_ofertas_inter).values_list('titulo',flat=True)
    print(nom_oe)
    ids_p_e = Intercambio.objects.filter(id__in=ids_ofertas_enviadas_aceptadas).values_list('id_publicacion',flat=True)
    n= Publicacion.objects.filter(id__in=ids_p_e).values_list('titulo',flat=True)

    mis=list(chain( nombre_mis,nom_oe))
    otros=list(chain( o,n))

    mostrar= intercambios1 | intercambios2
    
    combinadas = list(zip_longest(mostrar, mis, otros))

    #print(len(mostrar))
    #print(len(mis))
    #print(len(otros))

    contexto = {
        'mostrar': mostrar,
        'mis':mis,
        'otros':otros
    }
    return render (request, "historial.html", {'combinadas': combinadas})