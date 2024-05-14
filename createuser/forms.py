from django import forms
from .models import Usuario, Publicacion
from django.forms import TextInput

class UsuarioForm(forms.ModelForm):
    # Configuracion de los inputs como en html
    textInputDia = TextInput(attrs={"name" : "special", "placeholder": "Dia", "maxlength" : 2, "size" : 2})
    textInputMes = TextInput(attrs={"name" : "special", "placeholder": "Mes", "maxlength" : 2, "size" : 2})
    textInputAnio = TextInput(attrs={"name" : "special", "placeholder": "Año", "maxlength" : 4, "size" : 3})
    textInputNombre = TextInput(attrs={"placeholder": "Nombres", "maxlength" : 30})
    textInputApellido = TextInput(attrs={"placeholder": "Apellidos", "maxlength" : 20})
    textInputFecha = TextInput(attrs={"placeholder": "Fecha", "maxlength" : 20})
    textInputDNI = TextInput(attrs={"placeholder": "DNI", "maxlength" : 8})
    textInputCorreo = TextInput(attrs={"placeholder": "Correo", "maxlength" : 50})
    textInputPassword = TextInput(attrs={"type" : "password", "placeholder": "Contraseña", "maxlength" : 30})
    # Campos no relacionados al modelo
    dia = forms.CharField(widget=textInputDia, label="")
    mes = forms.CharField(widget=textInputMes, label="")
    anio = forms.CharField(widget=textInputAnio, label="")
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

class StaffForm(forms.ModelForm):
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