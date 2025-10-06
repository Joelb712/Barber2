from django.urls import path
from .views import *

urlpatterns = [
    path('horarios/', lista_horarios, name='lista_horarios'),
    path('horarios/nuevo/', crear_horario, name='formhora'),
    path('horarios/editar/<int:pk>/', editar_horario, name='editar_horario'),
    path('horarios/eliminar/<int:pk>/', eliminar_horario, name='eliminar_horario'),
    # path("reserva/servicios/", servicios_view, name="servicios"),
    # path("reserva/fechas/", fechas_view, name="fechas"),
    # path("reserva/empleados/", empleados_view, name="empleados"),
    # path("reserva/confirmar/", confirmar_turno, name="confirmar_turno"),
    path('turnos/', turnos_general, name='turnos'),
    # path('reserva/horarios-disponibles/', horarios_disponibles, name='horarios_disponibles'), 
    # path('solicitar-turno/', solicitar_turno, name='solicitar_turno'),
    path('api/servicios/', get_servicios, name='get_servicios'),
    path('api/barberos/', get_barberos, name='get_barberos'),
    path('api/horarios-disponibles/', get_horarios_disponibles, name='get_horarios_disponibles'),
    path('api/crear-turno/', crear_turno, name='crear_turno'),
]
