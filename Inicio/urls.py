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
    path('historial-turnos/', historial_turnos_empleado, name='historial_turnos'),
    path('datos-torta/', datos_torta, name='datos_torta'),
    path('datos-lineal/', datos_lineal, name='datos_lineal'),
    path('datos-turnos/', datos_turnos, name='datos_turnos'),
    path('datos-barberos/', datos_barberos_hoy_ajax, name='datos_barberos'),
]
