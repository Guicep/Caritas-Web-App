from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.db import models
import uuid
from datetime import datetime, timedelta

CONST_CODIGO_BASE = 1000

# Create your models here.

class CustomUserManager(UserManager):
    def _create_user(self, correo, password, **extra_fields):
        if not correo:
            raise ValueError("Users must have an email address")
        usuario = self.model(
            correo=self.normalize_email(correo),
            **extra_fields
        )
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, correo=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(correo, password, **extra_fields)

    def create_staff(self, correo, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(correo, password, **extra_fields)

    def create_admin(self, correo, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(correo, password, **extra_fields)

    def create_superuser(self, correo, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(correo, password, **extra_fields)
    
class Usuario(AbstractBaseUser, PermissionsMixin):
    correo = models.EmailField(blank=True, max_length=50, unique=True)
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=20)
    nacimiento = models.DateField()
    dni = models.CharField(max_length=8)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'correo'
    EMAIL_FIELD = 'correo'
    REQUIRED_FIELDS = ['nacimiento']


def get_default_fecha_acordada():
    return datetime.now().date() + timedelta(days=0)

class Intercambio(models.Model):
    id_publicacion = models.IntegerField()
    id_ofertante = models.IntegerField()
    fecha_acordada = models.DateField(default=get_default_fecha_acordada())
    estado = models.CharField(max_length=100)
    motivo_cancelacion = models.CharField(max_length=200, blank=True)
    codigo_intercambio = models.CharField(max_length=6)

class Publicacion(models.Model):
    titulo = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    fecha_publicacion = models.DateField(auto_now=True)
    foto = models.ImageField(upload_to='static/images/', null=True, blank=True)
    descripcion = models.CharField(max_length=200)
    id_usuario = models.IntegerField()
    oculto = models.BooleanField()
    finalizada = models.BooleanField()

class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    contenido = models.TextField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    respuesta = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='respuestas')
    respondido = models.BooleanField(default=False)

class Oferta(models.Model):
    id_publicacion = models.IntegerField()
    id_ofertante = models.IntegerField()
    titulo = models.CharField(max_length=100)
    cantidad = models.IntegerField(default=0)
    descripcion = models.CharField(max_length=200)
    aceptada = models.BooleanField()
    finalizada = models.BooleanField()

