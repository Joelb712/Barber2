from django.urls import path
from .views import *

urlpatterns = [
    path('horarios/', lista_horarios, name='lista_horarios'),
    path('horarios/tabla/',tabla_horarios, name='tabla_horarios'),
    path('horarios/nuevo/', crear_horario, name='formhora'),
    path('horarios/editar/<int:pk>/', editar_horario, name='editar_horario'),
    path('horarios/eliminar/<int:pk>/', eliminar_horario, name='eliminar_horario'),
    path('turnos/', turnos_general, name='turnos'),
    path('turnos/tabla/', tabla_turnos, name='tabla_turnos'),
    path('turnos/editar/<int:pk>/', editar_turno, name='editar_turno'),
    path('turnos/eliminar/<int:pk>/', eliminar_turno, name='eliminar_turno'),
    path('api/servicios/', get_servicios, name='get_servicios'),
    path('api/barberos/', get_barberos, name='get_barberos'),
    path('api/horarios-disponibles/', get_horarios_disponibles, name='get_horarios_disponibles'),
    path('api/crear-turno/', crear_turno, name='crear_turno'),
    path('darturno/', dar_turno, name='dar_turno'),
]
