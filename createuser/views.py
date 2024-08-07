from django.shortcuts import render, redirect
from .models import Usuario, Publicacion, Oferta, Intercambio, Comentario, Tarjeta,DonacionProducto,DonacionEfectivo,DonacionTarjeta, CodigosRecuperacion, ReseniasHabilitadas
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from .forms import UsuarioForm, PublicacionForm, LoginForm, StaffForm, ComentarioForm, TarjetaForm, DonacionProductoForm, EditProfileForm, DonacionTarjetaForm, DonacionEfectivoForm, RestablecerContraseñaForm, IngresarCodigoForm, CambiarContraseñaForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import os
from itertools import chain, zip_longest
from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.views.generic import DetailView

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
    resultados_ocultos_ofertante = Intercambio.objects.filter(id_ofertante__in=ofertas_usuario, estado='Pendiente').values_list("id_publicacion", flat=True)
    resultados_publicacion_ocultas = Publicacion.objects.filter(pk__in=resultados_ocultos_ofertante)
    resultados = Publicacion.objects.all().exclude(id_usuario=request.user.id).exclude(oculto=True).exclude(finalizada=True) | resultados_publicacion_ocultas
    
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
                            finalizada = False)
            publicacion.save()
            return redirect("welcome")
    else:
        return render(request, "publish.html", context)

def detalle_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, id=pk)
    comentarios = Comentario.objects.filter(publicacion=publicacion, respuesta__isnull=True)
    usuarios_ofertantes = Oferta.objects.filter(id_publicacion=pk).exclude(finalizada=True).values_list('id_ofertante', flat=True)
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
    suceso = "return confirm('¿Está seguro de borrar la publicación?')"
    urlprox = "borrar"
    if usuarios_ofertantes.count() > 0:
        suceso = "return alert('No se puede borrar por que existe una o mas ofertas')"
        urlprox = ""
    intercambio_query = Intercambio.objects.filter(id_publicacion=publicacion.pk).exclude(estado="Cancelado")
    if intercambio_query.exists():
        intercambio = intercambio_query.get()
    else:
        intercambio = None
    data = {
        'item': publicacion,
        'item2': intercambio,
        'comentarios': comentarios,
        'form': form,
        'respuesta_form': respuesta_form,
        'tiene_oferta': request.user.id in usuarios_ofertantes,
        'suceso': suceso,
        'urlprox': urlprox,
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
    print(user.correo)
    if(item.id_usuario == request.user.id or request.user.is_staff or request.user.is_superuser):
        send_mail(
            "Publicacion Eliminada",
            "Tu Publicacion: "+item.titulo+" a sido eliminada",
            "settings.EMAIL_HOST_USER",
            [user.correo])
        item.finalizada = True
        item.save()
        print("se envio correo a:", user.correo)
    if request.user.is_staff:
        return redirect('welcome')
    return redirect('ver_publicaciones')

def ver_publicaciones(request):
    mis_publicaciones=Publicacion.objects.filter(id_usuario=request.user.id).exclude(finalizada=True)
    data = {
        'item':mis_publicaciones
    }
    return render(request, 'ver_publicaciones.html', data)

def ofertas(request,pk):
    mis_ofertas = Oferta.objects.filter(id_publicacion=pk).exclude(finalizada=True)
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
        fec = request.POST.get('fecha')
        hrs = request.POST.get('hora')
        suc = request.POST.get('sucursal')
        Oferta.objects.create(
            id_publicacion = id_pu, 
            id_ofertante = id_of, 
            titulo = tit, 
            cantidad = cant, 
            descripcion = desc,
            fecha = fec,
            hora = hrs, 
            sucursal = suc,
            aceptada = False,
            finalizada = False,)
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
        send_mail(
            "Aviso de oferta aceptada!",
            "La oferta "+oferta.get().titulo+" en la publicación "+publicacion.get().titulo+
            " de "+publicante.get().apellido+" "+publicante.get().nombre +" a sido aceptada!\n\n"+
            "Su intercambio se realizara el dia "+resultado.get().fecha_acordada.strftime('%d/%m/%Y')+" con el codigo: "+
            resultado.get().codigo_intercambio+" en la filial de "+oferta.get().sucursal,
            "settings.EMAIL_HOST_USER",
            [publicante.get().correo, ofertante.get().correo],
        )
    return redirect("detalle_publicacion", pk=publicacion.get().pk)

def oferta_rechazada(request):
    motivo = request.POST.get('motivo')
    oferta = Oferta.objects.filter(pk=request.POST.get("oferta_id"))
    publicacion = Publicacion.objects.filter(pk=oferta.get().id_publicacion)
    publicante = Usuario.objects.filter(pk=publicacion.get().id_usuario)
    ofertante = Usuario.objects.filter(pk=oferta.get().id_ofertante)
    send_mail(
        "Aviso de oferta cancelada",
        "Su oferta "+oferta.get().titulo+" en la publicación "+publicacion.get().titulo+
        " de "+publicante.get().apellido+" "+publicante.get().nombre +" fue rechazada"+
        " por el motivo: "+motivo,
        "settings.EMAIL_HOST_USER",
        [ofertante.get().correo],
    )
    oferta.update(finalizada=True)
    return redirect('ofertas', pk=publicacion.get().pk)

def cancelar_intercambio(request, id):
    print(id)
    context = {}
    intercambio = Intercambio.objects.filter(id=id).exclude(estado='Cancelado')
    publicacion = Publicacion.objects.filter(pk=intercambio.get().id_publicacion)
    oferta = Oferta.objects.filter(pk=intercambio.get().id_ofertante)
    publicante = Usuario.objects.filter(pk=publicacion.get().id_usuario)
    ofertante = Usuario.objects.filter(pk=oferta.get().id_ofertante)
    intercambio.update(motivo_cancelacion=request.POST.get('motivo'))
    publicacion.update(oculto=False)
    oferta.update(finalizada=True)
    reseña_ambos = ReseniasHabilitadas(publicante = publicante.get(),
                                    ofertante = ofertante.get(),
                                    publicante_habilitado=True,
                                    ofertante_habilitado=True,)
    reseña_ambos.save()
    if request.POST.get('habilita_publicante'):
        send_mail('Califique al usuario de la oferta: ' + oferta.get().titulo,
                  'Fue habilitado para calificar al usuario ' + ofertante.get().nombre + 
                  ' lo puede hacer en el siguiente link:\n' +
                  'http://127.0.0.1:8000/calificar_usuario/?pk_o='+str(ofertante.get().pk)+'&review='+str(reseña_ambos.pk),
                  'settings.EMAIL_HOST_USER',
                  [publicante.get().correo])
    else:
        reseña_ambos.publicante_habilitado = False
        reseña_ambos.save()

    if request.POST.get('habilita_ofertante'):
        send_mail('Califique al usuario de la publicacion: ' + publicacion.get().titulo,
                  'Fue habilitado para calificar al usuario ' + publicante.get().nombre + 
                  ' lo puede hacer en el siguiente link:\n' +
                  'http://127.0.0.1:8000/calificar_usuario/?pk_p='+str(publicante.get().pk)+'&review='+str(reseña_ambos.pk),
                  'settings.EMAIL_HOST_USER',
                  [ofertante.get().correo])
    else:
        reseña_ambos.ofertante_habilitado = False
        reseña_ambos.save()
    send_mail(
        "Intercambio "+intercambio.get().codigo_intercambio+" cancelado",
        "El intercambio con codigo: " + intercambio.get().codigo_intercambio
        +" a sido cancelado por:\n\n" + intercambio.get().motivo_cancelacion, 
        "settings.EMAIL_HOST_USER", 
        [publicante.get().correo, ofertante.get().correo])
    intercambio.update(estado="Cancelado")
    context['mensaje'] = 'Cancelacion hecha con exito'
    return render(request, 'welcome.html', context)

def confirmar(request, id):
    context = {'id' : id}
    return render(request, "confirmar.html", context)

def confirmar_intercambio(request, id):
    context = {}
    intercambio = Intercambio.objects.filter(pk=id, estado='Pendiente')
    # Actualizar estado de oferta y publicación
    oferta = Oferta.objects.filter(pk=intercambio.get().id_ofertante)
    publicacion = Publicacion.objects.filter(pk=intercambio.get().id_publicacion)
    ofertante = Usuario.objects.filter(pk=oferta.get().id_ofertante)
    publicante = Usuario.objects.filter(pk=publicacion.get().id_usuario)
    reseña_ambos = ReseniasHabilitadas(publicante = publicante.get(),
                                    ofertante = ofertante.get(),
                                    publicante_habilitado=True,
                                    ofertante_habilitado=True,)
    reseña_ambos.save()
    send_mail(
        "Intercambio "+intercambio.get().codigo_intercambio+" confirmado!",
        "El intercambio con codigo: " + intercambio.get().codigo_intercambio
        +" a sido confirmado! gracias por utilizar nuestro servicio\n"
        +"En breve le llegara otro mail para calificar al otro usuario mediante un enlace", 
        "settings.EMAIL_HOST_USER", 
        [publicante.get().correo, ofertante.get().correo])
    send_mail('Califique al usuario de la publicacion: ' + publicacion.get().titulo,
        'Fue habilitado para calificar al usuario ' + publicante.get().nombre + 
        ' lo puede hacer en el siguiente link:\n' +
        'http://127.0.0.1:8000/calificar_usuario/?pk_p='+str(publicante.get().pk)+'&review='+str(reseña_ambos.pk),
        'settings.EMAIL_HOST_USER',
        [ofertante.get().correo])
    send_mail('Califique al usuario de la oferta: ' + oferta.get().titulo,
        'Fue habilitado para calificar al usuario ' + ofertante.get().nombre + 
        ' lo puede hacer en el siguiente link:\n' +
        'http://127.0.0.1:8000/calificar_usuario/?pk_o='+str(ofertante.get().pk)+'&review='+str(reseña_ambos.pk),
        'settings.EMAIL_HOST_USER',
        [publicante.get().correo])
    publicacion.update(finalizada=True)
    oferta.update(finalizada=True)
    intercambio.update(estado="Confirmado")
    context['mensaje'] = 'Confirmacion hecha con exito'
    return render(request, 'welcome.html', context)

def registrar_producto(request):
    context = {}
    if request.method == "POST":
        form = DonacionProductoForm(request.POST)
        if form.is_valid():
            donacion_producto = form.save(commit=False)
            donador = Usuario.objects.filter(dni=request.POST["dni_donante"])
            if donador.exists():
                donacion_producto.donante = donador.get()
            donacion_producto.save()
            messages.success(request, "Producto registrado correctamente")
            return redirect(reverse('registrar_producto') + '?success=True')
    else:
        form = DonacionProductoForm()

    context["forms"] = form
    return render(request, 'registrar_producto.html', context)

def restablecer_contraseña(request):
    context = {}
    if request.method == 'POST':
        context['forms'] = IngresarCodigoForm()
        correo_usuario = request.POST.get('correo')
        usuario_actual = Usuario.objects.filter(correo=correo_usuario)
        if usuario_actual.exists():
            codigo_vigente = CodigosRecuperacion.objects.filter(usuario=usuario_actual.get()).exclude(vencido=True)
            if codigo_vigente.exists():
                codigo_vigente.update(vencido=True)
            codigo_usuario = CodigosRecuperacion.objects.create(usuario=usuario_actual.get(), vencido=False)
            resultado = CodigosRecuperacion.objects.filter(pk=codigo_usuario.pk)
            resultado.update(codigo=100000+codigo_usuario.pk)
            send_mail("Codigo de recuperacion de cuenta",
                      "Su codigo es " + resultado.get().codigo,
                      "settings.EMAIL_HOST_USER",
                      [correo_usuario])
            context['correo'] = correo_usuario
        return render(request, 'confirmar_codigo.html', context)
    else:
        context['forms'] = RestablecerContraseñaForm()
        return render(request, 'restablecer.html', context)
    
def validar_codigo(request):
    context = {}
    if request.method == 'POST':
        context['forms'] = IngresarCodigoForm()
        codigo_usuario = request.POST.get('codigo')
        codigo_recuperacion = CodigosRecuperacion.objects.filter(codigo=codigo_usuario).exclude(vencido=True)
        if codigo_recuperacion.exists():
            codigo_recuperacion.update(vencido=True)
            context['correo'] = request.POST.get('correo')
            context['forms'] = CambiarContraseñaForm()
            return render(request, 'cambiar_contraseña.html', context)
        else:
            context['mensaje'] = 'El código no pudo ser validado'
            return render(request, 'confirmar_codigo.html', context)

def cambiar_contraseña(request):
    context = {}
    if request.method == 'POST':
        if request.user.is_authenticated:
            valid = True
            user = authenticate(request, username=request.user.correo, password=request.POST.get('contraseña_vieja'))
            if user is None and valid:
                valid = False
                context['mensaje'] = 'La contraseña actual es erronea'
                context['forms'] = CambiarContraseñaForm()
            if request.POST.get('contraseña_vieja') == request.POST.get('contraseña_nueva') and valid:
                valid = False
                context['mensaje'] = 'La contraseña actual y la nueva son iguales'
                context['forms'] = CambiarContraseñaForm()
            if not password_with_six_or_more_char(request.POST.get('contraseña_nueva')) and valid:
                valid = False
                context['mensaje'] = 'La contraseña debe tener 6 o mas characteres'
                context['forms'] = CambiarContraseñaForm()
            if request.POST.get('contraseña_nueva') != request.POST.get('contraseña_repetida') and valid:
                valid = False
                context['mensaje'] = 'Las contraseñas nuevas no son iguales'
                context['forms'] = CambiarContraseñaForm()
            if not valid:  
                return render(request, 'cambiar_contraseña.html', context)
            actualizar_usuario = Usuario.objects.get(correo=request.user.correo)
            actualizar_usuario.set_password(request.POST.get('contraseña_nueva'))
            actualizar_usuario.save()
            user = authenticate(request, username=request.user.correo
                                , password=request.POST.get('contraseña_nueva'))
            if user is not None:
                login(request, user)
            context['mensaje'] = 'La contraseña fue modificada con exito'
            context['usuario'] = request.user
            return render(request, 'perfil.html', context)
        else:
            valid = True
            if not password_with_six_or_more_char(request.POST.get('contraseña_nueva')) and valid:
                valid = False
                context['mensaje'] = 'La contraseña debe tener 6 o mas caracteres'
                context['forms'] = CambiarContraseñaForm()
            if request.POST.get('contraseña_nueva') != request.POST.get('contraseña_repetida') and valid:
                valid = False
                context['mensaje'] = 'Las contraseñas nuevas no son iguales'
                context['forms'] = CambiarContraseñaForm()
            if not valid:
                context['correo'] = request.POST.get('correo')
                return render(request, 'cambiar_contraseña.html', context)
            actualizar_usuario = Usuario.objects.get(correo=request.POST.get('correo'))
            actualizar_usuario.set_password(request.POST.get('contraseña_nueva'))
            actualizar_usuario.save()
            context['mensaje'] = 'La contraseña fue modificada con exito'
            context['forms'] = RestablecerContraseñaForm
            return render(request, 'restablecer.html', context)
    else:
        context['forms'] = CambiarContraseñaForm()
        return render(request, 'cambiar_contraseña.html', context)

@login_required
def calificar_usuario(request):
    context = {}
    if request.method == 'POST':
        resenia_habilitada = ReseniasHabilitadas.objects.get(pk=request.POST.get('review'))
        if request.POST.get('pk_o'):
            ofertante = Usuario.objects.get(pk=request.POST.get('pk_o'))
            ofertante.calificaciones_recibidas = ofertante.calificaciones_recibidas + 1
            ofertante.calificaciones_puntaje = ofertante.calificaciones_puntaje + int(request.POST.get('calificacion'))
            ofertante.calificacion_promedio = ofertante.calificaciones_puntaje / ofertante.calificaciones_recibidas
            ofertante.save()
            resenia_habilitada.publicante_habilitado = False
            resenia_habilitada.save()
        else:
            publicante = Usuario.objects.get(pk=request.POST.get('pk_p'))
            publicante.calificaciones_recibidas = publicante.calificaciones_recibidas + 1
            publicante.calificaciones_puntaje = publicante.calificaciones_puntaje + int(request.POST.get('calificacion'))
            publicante.calificacion_promedio = publicante.calificaciones_puntaje / publicante.calificaciones_recibidas
            publicante.save()
            resenia_habilitada.ofertante_habilitado = False
            resenia_habilitada.save()
        context['mensaje'] = 'Gracias por contrubuir con su puntuacion!'
        return render(request, 'calificar_usuario.html', context)
    else:
        resenia_habilitada = ReseniasHabilitadas.objects.get(pk=request.GET.get('review'))
        if request.GET.get('pk_o'):
            if resenia_habilitada.publicante_habilitado:
                context['habilitado'] = True
            else:
                context['habilitado'] = False
                context['mensaje'] = 'Usted ya califico al usuario'
        else:
            if resenia_habilitada.ofertante_habilitado:
                context['habilitado'] = True
            else:
                context['habilitado'] = False
                context['mensaje'] = 'Usted ya califico al usuario'
        return render(request, 'calificar_usuario.html', context)

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
    id_ou = Oferta.objects.filter(id_ofertante=request.user.id).values_list('pk',flat=True)
    # agaro ids de las ofertas enviadas por el usuario que han sido aceptadas 
    #ids_ofertas_enviadas_aceptadas = Intercambio.objects.filter(id_ofertante__in=Oferta.objects.filter(id_ofertante=request.user.id).values_list('id', flat=True)).values_list('id', flat=True)
    ids_ofertas_enviadas_aceptadas = Intercambio.objects.filter(id_ofertante__in=id_ou).values_list('pk',flat=True)
    ids_ofertas_inter = Intercambio.objects.filter(id_ofertante__in=id_ou).values_list('id_ofertante',flat=True)
    # aca agarro todas las id de publicaciones de los intercambios
    ids_publicaciones_intercambios = Intercambio.objects.filter().values_list('id_publicacion', flat=True)
    #aca tengo que agarra de las publicaciones que tienen intercambio y me guardo el id del usuario
    publicaciones_que_intercambios = Publicacion.objects.filter(id__in=ids_publicaciones_intercambios)
    #aca tengo publicaciones del usuario que son intercambios, o sea hay que mostrar
    publicaciones_del_usuario_quesonintercambio = publicaciones_que_intercambios.filter(id_usuario=request.user.id).values_list('id', flat=True)
    #ofertas recibidas que se transformaron en intercambio, ya estoy loco en este punto.
    ofertas_recibidas= Oferta.objects.filter(id_publicacion__in=publicaciones_del_usuario_quesonintercambio).values_list('id', flat=True)
    
    #sql = "SELECT p.titulo FROM createuser_publicacion p INNER JOIN createuser_intercambio i on p.id = i.id_publicacion INNER JOIN createuser_oferta o on i.id_ofertante = o.id"

    #cursor = connection.cursor()
    #cursor.execute(sql)
    #results = cursor.fetchall()

    intercambios1= Intercambio.objects.filter(id_ofertante__in=ofertas_recibidas)
    idsp = Intercambio.objects.filter(id_ofertante__in=ofertas_recibidas).values_list('id_publicacion',flat=True)
    idso = Intercambio.objects.filter(id_ofertante__in=ofertas_recibidas).values_list('id_ofertante',flat=True)
    nombre_mis = Publicacion.objects.filter(id__in=idsp).values_list('titulo',flat=True)
    nombre_mis2 = Publicacion.objects.filter(id__in=idsp).values_list('titulo',flat=True)
    lista = []
    for index in idsp:
        lista.append(Publicacion.objects.filter(id=index).values_list('titulo', flat=True))
    result_list = list(chain(*lista ))
    o = Oferta.objects.filter(id__in=idso).values_list('titulo', flat=True)
    intercambios2= Intercambio.objects.filter(id__in=ids_ofertas_enviadas_aceptadas)

    nom_oe = Oferta.objects.filter(id__in=ids_ofertas_inter).values_list('titulo',flat=True)
    ids_p_e = Intercambio.objects.filter(id__in=ids_ofertas_enviadas_aceptadas).values_list('id_publicacion',flat=True)
    lista2 = []
    for index in ids_p_e:
        lista2.append(Publicacion.objects.filter(id=index).values_list('titulo', flat=True))
    result_list2 = list(chain(*lista2))
    n= Publicacion.objects.filter(id__in=ids_p_e).values_list('titulo',flat=True)
    #lista_sin_parentesis = [tupla[0] for tupla in results]
    mis=list(chain( result_list,nom_oe))
    otros=list(chain( o, result_list2))
    mostrar= intercambios1 | intercambios2
    
    combinadas = list(zip_longest(mostrar, mis, otros))

    contexto = {
        'mostrar': mostrar,
        'mis':mis,
        'otros':otros
    }
    return render (request, "historial.html", {'combinadas': combinadas})

def listar_intercambios(request):
    hoy=date.today()
    codigos=Intercambio.objects.filter(fecha_acordada=hoy, estado='Pendiente')

    return render(request, "listar_intercambios.html",{'codigos': codigos})


def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id, usuario=request.user)
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ComentarioForm(instance=comentario)
        html = render_to_string('editar_comentario_modal.html', {'form': form, 'comentario': comentario}, request=request)
        return JsonResponse({'html': html})
    


def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id,)


    
    pk_actual=comentario.publicacion.pk
    comentario.delete()

    # Redirigir a la página de detalle de la publicación u otra página relevante
    return redirect('detalle_publicacion', pk=pk_actual)


def listar_donaciones(request):
    return render(request, "listar_donaciones.html")

def registrar_tarjeta(request):
    mensaje = ''
    form = TarjetaForm()
    if request.method == "POST":
        form = TarjetaForm(request.POST)
        numero_fechaactual = int(datetime.now().strftime("%Y-%m-%d").replace('-', ''))
        numero_validez = int(request.POST["validez"].replace('-', ''))
        if (numero_fechaactual+1) > numero_validez:
            mensaje = 'tarjeta expirada'
        else:
            if not Usuario.objects.filter(dni=request.POST["dni"]):
                mensaje = 'no existe el DNI en el sistema'
            else:
                if Tarjeta.objects.filter(dni=request.POST["dni"]):
                    mensaje = 'este DNI ya tiene una tarjeta asociada'
                else:
                    if form.is_valid():
                        form.save()
                        mensaje = 'Tarjeta registrada con exito'
    contexto = {
        'form': form,
        'mensaje': mensaje
    }
    return render(request, 'registrar_tarjeta.html', contexto)

@login_required
def perfil(request):
    usuario = request.user
    return render(request, 'perfil.html', {'usuario': usuario})

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f"{request.path}?saved=true")
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'editar_perfil.html', {'form': form})

def registrar_donacion_tarjeta(request):
    mensaje = ''
    form = DonacionTarjetaForm()
    if request.method == "POST":
        form = DonacionTarjetaForm(request.POST)
        if not Tarjeta.objects.filter(numero=request.POST["numero"], cvc=request.POST["cvc"]):
            mensaje = 'la tarjeta no existe o es incorrecta'
        else:
            saldo = Tarjeta.objects.filter(numero=request.POST["numero"]).values_list('monto',flat=True)[0]
            monto_donacion = int(request.POST["monto"])
            if saldo < monto_donacion:
                mensaje = 'tarjeta sin saldo'
            else:
                saldo = saldo - monto_donacion
                Tarjeta.objects.filter(numero=request.POST["numero"]).update(monto=saldo)
                if form.is_valid():
                    form.save()
                    mensaje = 'Donacion registrada con exito'
    contexto = {
        'form': form,
        'mensaje': mensaje
    }
    return render(request, 'registrar_donacion_tarjeta.html', contexto)


def registrar_donacion_efectivo(request):
    mensaje = ''
    form = DonacionEfectivoForm()
    if request.method == "POST":
        form = DonacionEfectivoForm(request.POST)
        if not Usuario.objects.filter(dni=request.POST["dni"]):
            mensaje = 'no existe el DNI en el sistema'
        else:
            if form.is_valid():
                form.save()
                mensaje = 'Donacion registrada con exito'
    contexto = {
        'form': form,
        'mensaje': mensaje
    }
    return render(request, 'registrar_donacion_efectivo.html', contexto)

def listar_donaciones(request):
    today = date.today()
    donaciones_producto = DonacionProducto.objects.filter(fecha__date=today)
    donaciones_tarjeta = DonacionTarjeta.objects.filter(fecha__date=today)
    donaciones_efectivo = DonacionEfectivo.objects.filter(fecha__date=today)

    tipo = request.GET.get('tipo')

    if tipo == 'producto':
        donaciones = donaciones_producto
    elif tipo == 'tarjeta':
        donaciones = donaciones_tarjeta
    elif tipo == 'efectivo':
        donaciones = donaciones_efectivo
    else:
        donaciones = list(donaciones_producto) + list(donaciones_tarjeta) + list(donaciones_efectivo)

    context = {
        'donaciones': donaciones,
        'tipo': tipo,
    }
    return render(request, 'listar_donaciones.html', context)


class UserDetailView(DetailView):
    model = Usuario
    template_name = 'usuario_detalle.html'
    context_object_name = 'usuario'

    def get_object(self):
        return get_object_or_404(Usuario, id=self.kwargs.get('pk'))                                      
def mostrar_inventario(request):
    donaciones_productos = DonacionProducto.objects.all()
    context = {
        'donaciones_productos': donaciones_productos
    }
    return render(request, 'mostrar_inventario.html', context)



def listar_donaciones_historica(request):
    donaciones_producto = DonacionProducto.objects.all()
    donaciones_tarjeta = DonacionTarjeta.objects.all()
    donaciones_efectivo = DonacionEfectivo.objects.all()

    tipo = request.GET.get('tipo')

    if tipo == 'producto':
        donaciones = donaciones_producto
    elif tipo == 'tarjeta':
        donaciones = donaciones_tarjeta
    elif tipo == 'efectivo':
        donaciones = donaciones_efectivo
    else:
        donaciones = list(donaciones_producto) + list(donaciones_tarjeta) + list(donaciones_efectivo)

    context = {
        'donaciones': donaciones,
        'tipo': tipo,
    }
    return render(request, 'listar_donaciones_historica.html', context)