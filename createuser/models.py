from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.db import models

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



class Publicacion(models.Model):
    titulo = models.CharField(max_length=100)
    foto = models.ImageField()
    descripcion = models.CharField(max_length=200)
    id_usuario = models.IntegerField()
