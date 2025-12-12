from datetime import datetime
from itertools import count
from django.http import HttpResponse
from django.shortcuts import render
from .models import User, Paciente, Investigador, EnsayoClinico
from arodj.forms import EnsayoClinicoFormRequest, EnsayoClinicoForm
from django.db.models import Q, Prefetch
from django.views.defaults import page_not_found, server_error, permission_denied, bad_request
from arodj.forms import RegistroForm, EnsayoClinicoBusquedaAvanzadaForm
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
            if (rol == User.PACIENTE):
                grupo = Group.objects.get(name='Pacientes')
                grupo.user_set.add(usuario)
                paciente = Paciente.objects.create(
                    user=usuario,
                    edad=form.cleaned_data.get('edad')
                )
                paciente.save()
            elif (rol == User.INVESTIGADOR):
                grupo = Group.objects.get(name='Investigadores')
                grupo.user_set.add(usuario)
                investigador = Investigador.objects.create(user=usuario)
                investigador.save()
            messages.success(request, 'Usuario registrado correctamente.')
            login(request, usuario)
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'registration/signup.html', {'form': form})

def lista_ensayos(request):
    ensayos = EnsayoClinico.objects.all()
    return render(request, 'arodj/lista_ensayos.html', {'ensayos': ensayos})    

@permission_required('arodj.add_ensayoclinico')
def ensayo_create(request):
    datosensayo= None
    if request.method == 'POST':
        datosensayo = request.POST
        
    formulario_e = EnsayoClinicoForm(datosensayo)
    
    if (request.method == 'POST'):
        formulario_creado = ensayo_crear(formulario_e)
        if (formulario_creado):
            messages.success(request, 'Ensayo clínico creado correctamente.')
            return redirect('lista_ensayos')
    return render(request, 'arodj/crear_ensayo.html', {'formulario_e': formulario_e})

@permission_required('arodj.add_ensayoclinico')
def ensayo_crear(formulario_e):
    formulario_creado = False
    if formulario_e.is_valid():
        try:
            formulario_e.save()
            formulario_creado = True
        except Exception as e:
            print(f"Error al crear el ensayo clínico: {e}")
            pass
    return formulario_creado

@permission_required('arodj.add_ensayoclinico')
def ensayo_create_generico_con_request(request):
    datosensayo= None
    if request.method == 'POST':
        datosensayo = request.POST
        
    formulario_e = EnsayoClinicoFormRequest(datosensayo, request=request)
    
    if (request.method == 'POST'):
        formulario_creado = ensayo_crear(formulario_e)
        if (formulario_creado):
            messages.success(request, 'Ensayo clínico creado correctamente.')
            return redirect('lista_ensayos', usuario=request.user.id)
    
    return render(request, 'arodj/crear_ensayo.html', {'formulario_e': formulario_e})

@permission_required('arodj.view_ensayoclinico')
def ensayo_busqueda_avanzada(request):
    QSensayos = EnsayoClinico.objects.all()
    #filtro segun el usuario logeado
    if request.user.is_authenticated and request.user.rol == User.INVESTIGADOR:
        investigador_usuario = Investigador.objects.filter(user=request.user).first() # obtener el investigador asociado al usuario
        if investigador_usuario is not None: # esto evita errores si no hay investigador asociado
            QSensayos = QSensayos.filter(creado_por=investigador_usuario)
    elif request.user.is_authenticated and request.user.rol == User.PACIENTE:
        paciente_usuario = Paciente.objects.filter(user=request.user).first() # obtener el paciente asociado al usuario
        if paciente_usuario is not None: # esto evita errores si no hay paciente asociado
            QSensayos = QSensayos.filter(pacientes=paciente_usuario)
    
    if (len(request.GET) > 0):
        formulario_busqueda_avanzada = EnsayoClinicoBusquedaAvanzadaForm(request.GET, user=request.user)
        if (formulario_busqueda_avanzada.is_valid()):
            #obtenemos los filtros
            texto = formulario_busqueda_avanzada.cleaned_data.get('texto')
            fecha_desde = formulario_busqueda_avanzada.cleaned_data.get('fecha_desde')
            fecha_hasta = formulario_busqueda_avanzada.cleaned_data.get('fecha_hasta')
            nivel_seguimiento_min = formulario_busqueda_avanzada.cleaned_data.get('nivel_seguimiento_min')
            pacientes = formulario_busqueda_avanzada.cleaned_data.get('pacientes')
            activo = formulario_busqueda_avanzada.cleaned_data.get('activo')
            
            #Por cada filtro comprobamos si tiene un valor y lo añadimos a la QuerySet
            if texto != '':
                QSensayos = QSensayos.filter(
                    Q(nombre__icontains=texto) | Q(descripcion__icontains=texto)
                )
            if fecha_desde is not None:
                QSensayos = QSensayos.filter(fecha_inicio__gte=fecha_desde)
            if fecha_hasta is not None:
                QSensayos = QSensayos.filter(fecha_inicio__lte=fecha_hasta)
            if nivel_seguimiento_min is not None:
                QSensayos = QSensayos.filter(nivel_seguimiento__gte=nivel_seguimiento_min)
            if pacientes.count() > 0:
                for paciente in pacientes:
                    QSensayos = QSensayos.filter(pacientes=paciente)
            if activo:
                QSensayos = QSensayos.filter(activo=True)
            ensayos_encontrados = QSensayos.all()
            return render(request, 'arodj/ensayo_busqueda.html', {
                'formulario_busqueda_avanzada': formulario_busqueda_avanzada,
                'ensayos': ensayos_encontrados,
            })
        else:
            ensayos_encontrados = QSensayos.all()
    else:
        ensayos_encontrados = QSensayos.all()
        formulario_busqueda_avanzada = EnsayoClinicoBusquedaAvanzadaForm(None, user=request.user) # pasar el usuario al formulario
    return render(request, 'arodj/ensayo_busqueda_avanzada.html', {
        'formulario_busqueda_avanzada': formulario_busqueda_avanzada,
        'ensayos': ensayos_encontrados,
    })
#5. Edición de Ensayo (1 punto)
#Debe tenerse en cuenta que validaciones no podemos aplicar en el momento de editar.Pista: hay dos casos.
#Solo puede editar los ensayos el investigador que haya creado el ensayo
@permission_required('arodj.change_ensayoclinico')
def ensayo_update(request, ensayo_id):
    ensayo = EnsayoClinico.objects.get(id=ensayo_id)
    datosensayo= None
    if request.method == 'POST':
        datosensayo = request.POST
        
    formulario_e = EnsayoClinicoForm(datosensayo, instance=ensayo)
    
    if (request.method == 'POST'):
        if formulario_e.is_valid():
            try:
                formulario_e.save()
                messages.success(request, 'Ensayo clínico actualizado correctamente.')
                return redirect('lista_ensayos')
            except Exception as e:
                pass  
    return render(request, 'arodj/crear_ensayo.html', {'formulario_e': formulario_e, 'ensayo': ensayo})

#6. Eliminación de Ensayo (1 punto)
#Debe tenerse en cuenta que validaciones no podemos aplicar en el momento de editar.Pista: hay dos casos.
#Solo puede eliminar los ensayos el investigador que haya creado el ensayo

@permission_required('arodj.delete_ensayoclinico')
def ensayo_delete(request, ensayo_id):
    ensayo = EnsayoClinico.objects.get(id=ensayo_id)
    
    try:
        ensayo.delete()
        messages.success(request, 'Ensayo clínico eliminado correctamente.')
        return redirect('lista_ensayos')
    except Exception as e:
        pass
    return redirect('lista_ensayos')
