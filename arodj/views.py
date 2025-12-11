from datetime import datetime
from itertools import count
from django.http import HttpResponse
from django.shortcuts import render
from .models import User, Cliente, Trabajador
from django.db.models import Q, Prefetch
from django.views.defaults import page_not_found, server_error, permission_denied, bad_request
from arodj.forms import RegistroForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import permission_required
#Importar Group
from django.contrib.auth.models import Group

# Create your views here.

def home(request):
    # eliminar si usuario no autenticado
    if not request.user.is_authenticated:
        if "fecha_inicio" in request.session:
            del request.session["fecha_inicio"]
        if "contador_visitas" in request.session:
            del request.session["contador_visitas"]
        if "rol_usuario" in request.session:
            del request.session["rol_usuario"]
        if "usuario_actual" in request.session:
            del request.session["usuario_actual"]
        # 1. Fecha de inicio de sesión
    else:
        if "fecha_inicio" not in request.session:
            request.session["fecha_inicio"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 2. Contador de visitas
        if "contador_visitas" not in request.session:
            request.session["contador_visitas"] = 1
        else:
            request.session["contador_visitas"] += 1
        # 3. Rol del usuario
        if request.user.is_authenticated: 
            request.session["rol_usuario"] = request.user.get_rol_display()
        else:
            request.session["rol_usuario"] = "Sin grupo"
        # 4. Nombre del usuario que ha renderizado la página
        request.session["usuario_actual"] = request.user.username
    
    return render(request, 'arodj/home.html', {})

#Sesiones
def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            rol = int(form.cleaned_data.get('rol'))
            if (rol == User.CLIENTE):
                grupo = Group.objects.get(name='Clientes')
                grupo.user_set.add(usuario)
                cliente = Cliente.objects.create(user=usuario)
                cliente.save()
            elif (rol == User.TRABAJADOR):
                grupo = Group.objects.get(name='Trabajadores')
                grupo.user_set.add(usuario)
                trabajador = Trabajador.objects.create(user=usuario)
                trabajador.save()
            messages.success(request, 'Usuario registrado correctamente.')
            login(request, usuario)
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'registration/signup.html', {'form': form})