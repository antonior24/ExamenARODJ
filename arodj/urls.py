from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ensayos/', views.lista_ensayos, name='lista_ensayos'),
    #CRUD CREATE
    path('ensayos/crear/', views.ensayo_create_generico_con_request, name='ensayo_create'),
    path('ensayos/crear_generico/', views.ensayo_create, name='ensayo_create_generico'),
    #CRUD READ
    
    
    #CRUD READ avanzado
    path('ensayos/buscar/', views.ensayo_busqueda_avanzada, name='ensayo_busqueda_avanzada'),
    
    #CRUD UPDATE
    path('ensayos/editar/<int:ensayo_id>/', views.ensayo_update, name='ensayo_update'),
    #CRUD DELETE
    path('ensayos/eliminar/<int:ensayo_id>/', views.ensayo_delete, name='ensayo_delete'),
    #Sessions
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    
    # Create Order with user association
    
    # lista de pedidos con usuario asociado
    
]