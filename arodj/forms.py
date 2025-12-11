from django import forms
from .models import User, Cliente, Trabajador
from django.contrib.auth.forms import UserCreationForm
from datetime import date, timedelta

#Formulario de registro de usuario
class RegistroForm(UserCreationForm):
    roles = (
            (User.CLIENTE, 'Cliente'),
            (User.TRABAJADOR, 'Trabajador'),
    )
    rol = forms.ChoiceField(choices=roles)
    #phone = forms.CharField(required=False)  # 👈 NO es obligatorio
    class Meta:
        model = User
        fields = ['username', 'email', 'rol', 'password1', 'password2']