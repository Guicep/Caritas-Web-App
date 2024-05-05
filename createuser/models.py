from django.db import models

# Create your models here.

class Usuario(models.Model):
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=20)
    nacimiento = models.DateField()
    dni = models.CharField(max_length=8)
    correo = models.CharField(max_length=50)
    password = models.CharField(max_length=30)