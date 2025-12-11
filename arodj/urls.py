from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    #CRUD CREATE
    
    
    #CRUD READ
    
    
    #CRUD READ avanzado
    
    #CRUD UPDATE
    
    #CRUD DELETE
    
    #Sessions
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    
    # Create Order with user association
    
    # lista de pedidos con usuario asociado
    
]