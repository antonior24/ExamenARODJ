from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
#importar para las sesiones
from django.contrib.auth.models import AbstractUser
# Create your models here.

#Usuarios
class User(AbstractUser):
    ADMINISTRADOR = 1
    CLIENTE = 2
    TRABAJADOR = 3
    
    ROLES = (
        (ADMINISTRADOR, 'Administrador'),
        (CLIENTE, 'Cliente'),
        (TRABAJADOR, 'Trabajador'),
    )
    
    rol = models.PositiveSmallIntegerField(choices=ROLES, default=1)
    
class Trabajador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)