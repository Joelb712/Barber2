from django.urls import path
from .views import *

urlpatterns=[
    path('',Inicio,name='Inicio'),
    path('dash',dash,name='dash'),
    path('contacto/',contacto,name='contacto'),
    path('tienda/',tienda,name='tienda'),
    path('reservar_turno/', reservar_turno, name='reservar_turno'),
    path('horarios_disponibles/',horarios_disponibles, name='horarios_disponibles'),
]
