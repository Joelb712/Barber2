from django.urls import path
from .views import *


urlpatterns=[
    path('',Inicio,name='Inicio'),
    path('dash',dash,name='dash'),
    path('contacto/',contacto,name='contacto'),
    path('misturnos/',mis_turnos,name='mis_turnos'),
    path('perfil/',perfil_cliente,name='perfil_cliente'),
    path('turnos/cancelar/<int:turno_id>/', cancelar_turno, name='cancelar_turno'),
    path('home/',home_empleado,name='home'),
    path('mi-perfil/', mi_perfil, name='mi_perfil'),
]
