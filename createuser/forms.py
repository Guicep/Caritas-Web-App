from django import forms
from .models import Usuario, Publicacion, Comentario, Intercambio, Tarjeta, DonacionProducto
from django.forms import TextInput
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate

class UsuarioForm(forms.ModelForm):
    # Configuracion de los inputs como en html
    textInputDia = forms.Select(attrs={"name" : "special"})
    textInputMes = forms.Select(attrs={"name" : "special"})
    textInputAnio = forms.Select(attrs={"name" : "special"})
    textInputNombre = TextInput(attrs={"placeholder": "Nombres", "maxlength" : 30})
    textInputApellido = TextInput(attrs={"placeholder": "Apellidos", "maxlength" : 20})
    textInputFecha = TextInput(attrs={"placeholder": "Fecha", "maxlength" : 20})
    textInputDNI = TextInput(attrs={"placeholder": "DNI", "maxlength" : 8})
    textInputCorreo = TextInput(attrs={"placeholder": "Correo", "maxlength" : 50})
    textInputPassword = TextInput(attrs={"type" : "password", "placeholder": "Contraseña", "maxlength" : 30})
    # Campos no relacionados al modelo
    dia = forms.ChoiceField(widget=textInputDia, choices=[(x, x) for x in range(1, 32)])
    # dia = forms.CharField(widget=textInputDia, label="")
    mes = forms.ChoiceField(widget=textInputDia, choices=[(x, x) for x in range(1, 13)])
    anio = forms.ChoiceField(widget=textInputDia, choices=[(x, x) for x in range(1950, 2024)])
    # Asignacion de la configuracion
    nombre = forms.CharField(widget=textInputNombre, label='')
    apellido = forms.CharField(widget=textInputApellido, label='')
    dni = forms.CharField(widget=textInputDNI, label='')
    correo = forms.CharField(widget=textInputCorreo, label='')
    password = forms.CharField(widget=textInputPassword, label='')
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'dni', 'correo', 'password']

class PublicacionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
    # Configuracion de los inputs como en html
    categorias =(('Comida', 'Comida'), ('Limpieza', 'Limpieza'), ('Ropa', 'Ropa'))
    textInputTitulo = TextInput(attrs={"placeholder": "Titulo", "maxlength" : 100})
    textInputDescripcion = forms.Textarea(attrs={"placeholder": "Descripcion", "maxlength" : 200, "rows":"5"})
    # Campos no relacionados al modelo
    # Asignacion de la configuracion
    titulo = forms.CharField(widget=textInputTitulo, label='')
    descripcion = forms.CharField(widget=textInputDescripcion, label='')
    categoria = forms.ChoiceField(choices=categorias, initial='1')
    foto = forms.ImageField(label='Foto del producto')
    class Meta:
        model = Publicacion
        fields = ['titulo', 'descripcion', 'categoria', 'foto']

class LoginForm(forms.Form):
    # Configuracion de los inputs como en html
    textInputCorreo = TextInput(attrs={"placeholder": "Usuario", "maxlength" : 50, "name" : "username"})
    textInputPassword = TextInput(attrs={"type" : "password", "placeholder": "Contraseña", "maxlength" : 30, "name" : "password"})
    # Campos
    correo = forms.CharField(widget=textInputCorreo, label='')
    password = forms.CharField(widget=textInputPassword, label='')

class StaffForm(forms.Form):
    # Configuracion de los inputs como en html
    textInputNombre = TextInput(attrs={"placeholder": "Nombres", "maxlength" : 30})
    textInputApellido = TextInput(attrs={"placeholder": "Apellidos", "maxlength" : 20})
    textInputCorreo = TextInput(attrs={"placeholder": "Correo", "maxlength" : 50})
    textInputPassword = TextInput(attrs={"type" : "password", "placeholder": "Contraseña", "maxlength" : 30})

    # Asignacion de la configuracion
    nombre = forms.CharField(widget=textInputNombre, label='')
    apellido = forms.CharField(widget=textInputApellido, label='')
    correo = forms.CharField(widget=textInputCorreo, label='')
    password = forms.CharField(widget=textInputPassword, label='')
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'correo', 'password']

#class ComentarioForm(forms.ModelForm):
#   class Meta:
#        model = Comentario
#        fields = ['id_publicacion', 'id_usuario', 'id_respuesta', 'contenido']
#        widgets = {
#            'id_publicacion': forms.HiddenInput(),
#            'id_usuario': forms.HiddenInput(),
#            'id_respuesta': forms.HiddenInput(),
#        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'placeholder': 'Escribe tu comentario aquí...'})
        }
        labels = {
            'contenido': ''  # Esto elimina la etiqueta del campo
        }

class IntercambioForm(forms.ModelForm):
    class Meta:
        model = Intercambio
        fields = ['id_publicacion', 'id_ofertante', 'fecha_acordada', 'estado', 'motivo_cancelacion']


class TarjetaForm(forms.ModelForm):
    # Configuracion de los inputs como en html
    textInput_id_usuario = TextInput(attrs={"type": "number", "maxlength": 30})
    textInput_numero = TextInput(attrs={"type": "number", "maxlength": 16})
    textInput_validez = TextInput(attrs={"type": "Date"})
    textInput_titular = TextInput(attrs={"type": "text", "maxlength": 150})
    textInput_cvc = TextInput(attrs={"type": "number", "maxlength": 3})
    textInput_tipo = (('Mastercard', 'Mastercard'), ('Visa', 'Visa'), ('AmericanExpres', 'AmericanExpres'))

    # Asignacion de la configuracion
    id_usuario = forms.CharField(widget=textInput_id_usuario, label='id usuario')
    numero = forms.CharField(widget=textInput_numero, label='numero de tarjeta')
    validez = forms.CharField(widget=textInput_validez, label='validez')
    titular = forms.CharField(widget=textInput_titular, label='titular')
    cvc = forms.CharField(widget=textInput_cvc, label='cvc')
    tipo = forms.ChoiceField(choices=textInput_tipo, initial='1')

    class Meta:
        model = Tarjeta
        fields = ['id_usuario', 'numero', 'validez', 'titular', 'cvc', 'tipo']

class DonacionProductoForm(forms.ModelForm):
    # Configuracion de los inputs como en html
    textInput_nombre_producto = TextInput(attrs={"placeholder": "Nombre de producto", "maxlength": 30})
    textInput_cantidad = TextInput(attrs={"placeholder": "Cantidad", "maxlength": 16})
    textInput_donante_nombre = TextInput(attrs={"placeholder": "Nombre del donante"})
    textInput_donante_apellido = TextInput(attrs={"placeholder": "Apellido del donante", "maxlength": 150})
    textInput_dni_apellido = TextInput(attrs={"placeholder": "DNI del donante", "maxlength": 8})

    # Asignacion de la configuracion
    nombre_producto = forms.CharField(widget=textInput_nombre_producto, label='')
    cantidad = forms.IntegerField(widget=textInput_cantidad, label='')
    nombre_donante = forms.CharField(widget=textInput_donante_nombre, label='')
    apellido_donante = forms.CharField(widget=textInput_donante_apellido, label='')
    dni_donante = forms.IntegerField(widget=textInput_dni_apellido, required=False, label='')

    class Meta:
        model = DonacionProducto
        fields = ['nombre_producto', 'cantidad', 'nombre_donante', 'apellido_donante']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['correo', 'nombre', 'apellido', 'nacimiento', 'dni']
        widgets = {
            'nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

        

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exists() and self.instance.correo != correo:
            raise forms.ValidationError("Este correo ya está en uso.")
        return correo
    
    def clean_nacimiento(self):
        nacimiento = self.cleaned_data.get('nacimiento')
        if nacimiento:
            if nacimiento < date(1950, 1, 1) or nacimiento > date(2006, 12, 31):
                raise ValidationError("La fecha de nacimiento debe estar entre 01/01/1950 y 31/12/2006.")
        return nacimiento
    
