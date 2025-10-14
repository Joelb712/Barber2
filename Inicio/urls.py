from django.urls import path
from .views import *


urlpatterns=[
    path('',Inicio,name='Inicio'),
    path('dash',dash,name='dash'),
    path('contacto/',contacto,name='contacto'),
    path('turnos/',mis_turnos,name='mis_turnos'),
    path('perfil/',perfil_cliente,name='perfil_cliente'),
    path('turnos/cancelar/<int:turno_id>/', cancelar_turno, name='cancelar_turno'),

]
