from django.contrib import admin
from .models import (
    User,
    Paciente,
    Investigador,
    Farmaco,
    EnsayoClinico,
    
)
# Register your models here.
admin.site.register(User)
admin.site.register(Paciente)
admin.site.register(Investigador)
admin.site.register(Farmaco)
admin.site.register(EnsayoClinico)