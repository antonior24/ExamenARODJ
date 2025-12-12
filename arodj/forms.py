from django import forms
from .models import User, Paciente, Investigador, Farmaco, EnsayoClinico
from django.contrib.auth.forms import UserCreationForm
from datetime import date, timedelta

#Formulario de registro de usuario
class RegistroForm(UserCreationForm):
    roles = (
            (User.PACIENTE, 'Paciente'),
            (User.INVESTIGADOR, 'Investigador'),
    )
    rol = forms.ChoiceField(choices=roles)
    edad = forms.IntegerField(required=False)  # 👈 NO es obligatorio
    class Meta:
        model = User
        fields = ['username', 'email', 'rol', 'edad', 'password1', 'password2']

#Registrar investigador que crea el ensayo desde la sesión (Investigador): (0,5 puntos)
#Modelo EnsayoClinico y validaciones (3 puntos)
#Los alumnos deben implementar formularios con las siguientes validaciones:
#Nombre único: (0,5 puntos)

#Descripción ≥ 100 caracteres: (0,2 puntos)

#Fármaco apto: (0,5 puntos)

#Pacientes mayores de edad: (0,5 puntos)

#Nivel de seguimiento 0-10: (0,2 puntos)

#Fecha inicio < fecha fin: (0,3 puntos)

#Fecha fin ≥ hoy: (0,3 puntos)
#hacer igual que ejemplo de OrderFormRequest

class EnsayoClinicoForm(forms.ModelForm):
    class Meta:
        model = EnsayoClinico
        fields = ['nombre', 'descripcion', 'farmaco', 'pacientes', 'nivel_seguimiento', 'fecha_inicio', 'fecha_fin', 'activo', 'creado_por']
        widgets = {
            'pacientes': forms.CheckboxSelectMultiple(),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'},format='%Y-%m-%d'),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'},format='%Y-%m-%d'),
        }
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        descripcion = cleaned_data.get('descripcion')
        farmaco = cleaned_data.get('farmaco')
        pacientes = cleaned_data.get('pacientes')
        nivel_seguimiento = cleaned_data.get('nivel_seguimiento')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')  
        creado_por = cleaned_data.get('creado_por')
        
        if nombre and EnsayoClinico.objects.filter(nombre=nombre).exists():
            self.add_error('nombre', 'El nombre del ensayo clínico ya existe.')
        if descripcion and len(descripcion) < 100:
            self.add_error('descripcion', 'La descripción debe tener al menos 100 caracteres.')
        if farmaco and not farmaco.apto_para_ensayos:
            self.add_error('farmaco', 'El fármaco seleccionado no es apto para ensayos clínicos.')
        if nivel_seguimiento is not None and (nivel_seguimiento < 0 or nivel_seguimiento > 10):
            self.add_error('nivel_seguimiento', 'El nivel de seguimiento debe estar entre 0 y 10.')
        if fecha_inicio and fecha_fin:
            if fecha_inicio >= fecha_fin:
                self.add_error('fecha_fin', 'La fecha de fin debe ser posterior a la fecha de inicio.')
            if fecha_fin < date.today():
                self.add_error('fecha_fin', 'La fecha de fin no puede ser anterior a hoy.')
        
        return cleaned_data


class EnsayoClinicoFormRequest(EnsayoClinicoForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(EnsayoClinicoFormRequest, self).__init__(*args, **kwargs)
        # Filtrar los pacientes mayores de edad
        pacientes_mayores = Paciente.objects.filter(edad__gte=18)
        self.fields["pacientes"] = forms.ModelMultipleChoiceField(
            queryset=pacientes_mayores,
            widget=forms.CheckboxSelectMultiple,
            required=True,
        )
     #  Controlar el campo 'creado_por' según el rol INVESTIGADOR
     #Error al crear el ensayo clínico: NOT NULL constraint failed: arodj_ensayoclinico.creado_por_id
        if self.request.user.is_authenticated:
            usuario = self.request.user

            # Si es INVESTIGADOR: fijamos su Investigador y ocultamos el campo
            if usuario.rol == User.INVESTIGADOR:
                investigador_qs = Investigador.objects.filter(user=usuario)
                if investigador_qs.exists():
                    self.fields["creado_por"] = forms.ModelChoiceField(
                        queryset=investigador_qs,
                        widget=forms.HiddenInput(),
                        initial=investigador_qs.first().id
                    )
            
#Búsqueda avanzada (2.5 puntos)
#Filtros que deben implementar:
#Que contenga un texto en nombre o descripción: (0,2 puntos)

#Fecha desde y fecha hasta del inicio del ensayo a la indicada: (0,3 puntos)

#Nivel de seguimiento mayor a un valor : (0,2 puntos)

#Selección múltiple de pacientes:  (0,4 puntos)

#Ensayos activos:  (0,4 puntos)

#Restricción por usuario logueado:
#Investigador: solo ve los ensayos que haya creado (0,5 puntos)

#Paciente: solo ve ensayos en los que está incluido (0,5 puntos)

class EnsayoClinicoBusquedaAvanzadaForm(forms.Form):
    texto = forms.CharField(required=False)
    nombre = forms.CharField(required=False)
    descripcion = forms.CharField(required=False)
    fecha_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    nivel_seguimiento_min = forms.IntegerField(required=False, min_value=0, max_value=10)
    pacientes = forms.ModelMultipleChoiceField(queryset=Paciente.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    activo = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # 🟦 Si el usuario está logueado como paciente → ocultamos el campo como hidden
        if user and user.is_authenticated and user.rol == User.PACIENTE:
            paciente_qs = Paciente.objects.filter(user=user)
            if paciente_qs.exists():
                self.fields["pacientes"].queryset = paciente_qs
                self.fields["pacientes"].initial = paciente_qs
            self.fields["pacientes"].widget = forms.HiddenInput()
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        descripcion = cleaned_data.get('descripcion')
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        nivel_seguimiento_min = cleaned_data.get('nivel_seguimiento_min')
        
        if (nombre == '' and descripcion == '' and fecha_desde is None and fecha_hasta is None and nivel_seguimiento_min is None):
            self.add_error('nombre', "Debe rellenar al menos un campo para la búsqueda avanzada.")
            self.add_error('descripcion', "")
            self.add_error('fecha_desde', "")
            self.add_error('fecha_hasta', "")
            self.add_error('nivel_seguimiento_min', "")
        else:
            if fecha_desde and fecha_hasta and fecha_hasta < fecha_desde:
                self.add_error('fecha_hasta', "La fecha hasta debe ser posterior o igual a la fecha desde.")
        
        return cleaned_data
        
