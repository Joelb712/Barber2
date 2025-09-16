from django.urls import path
from .views import *

urlpatterns = [
    path('horarios/', lista_horarios, name='lista_horarios'),
    path('horarios/nuevo/', crear_horario, name='formhora'),
    path('horarios/editar/<int:pk>/', editar_horario, name='editar_horario'),
    path('horarios/eliminar/<int:pk>/', eliminar_horario, name='eliminar_horario'),
    path("reserva/servicios/", servicios_view, name="servicios"),
    path("reserva/fechas/", fechas_view, name="fechas"),
    path("reserva/empleados/", empleados_view, name="empleados"),
    path("reserva/confirmar/", confirmar_turno, name="confirmar_turno"),
    path('turnos/', turnos_general, name='turnos'),
]
