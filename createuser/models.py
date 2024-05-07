from django.db import models

# Create your models here.

class Usuario(models.Model):
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=20)
    nacimiento = models.DateField()
    dni = models.CharField(max_length=8)
    correo = models.CharField(max_length=50)
    password = models.CharField(max_length=30)

class Publicacion(models.Model):
    titulo = models.CharField(max_length=100)
    foto = models.ImageField()
    descripcion = models.CharField(max_length=200)
    id_usuario = models.IntegerField()