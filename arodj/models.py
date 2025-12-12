from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
#importar para las sesiones
from django.contrib.auth.models import AbstractUser
# Create your models here.

#Usuarios
class User(AbstractUser):
    ADMINISTRADOR = 1
    PACIENTE = 2
    INVESTIGADOR = 3
    
    ROLES = (
        (ADMINISTRADOR, 'Administrador'),
        (PACIENTE, 'Paciente'),
        (INVESTIGADOR, 'Investigador'),
    )
    
    rol = models.PositiveSmallIntegerField(choices=ROLES, default=1)
    
class Investigador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    edad = models.IntegerField(null=True, blank=True)

class Farmaco(models.Model):
   nombre = models.CharField(max_length=100)
   apto_para_ensayos = models.BooleanField()
   def __str__(self):
       return self.nombre
class EnsayoClinico(models.Model):
   nombre = models.CharField(max_length=100)
   descripcion = models.TextField()
   farmaco = models.ForeignKey(Farmaco, on_delete=models.CASCADE)
   pacientes = models.ManyToManyField('Paciente')
   nivel_seguimiento = models.IntegerField()
   fecha_inicio = models.DateField()
   fecha_fin = models.DateField()
   activo = models.BooleanField(default=True)
   creado_por = models.ForeignKey('Investigador', on_delete=models.CASCADE)  
   def __str__(self):
       return self.nombre

