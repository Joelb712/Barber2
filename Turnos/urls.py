from django.urls import path
from .views import *

urlpatterns = [
    path('horarios/', lista_horarios, name='lista_horarios'),
    path('horarios/nuevo/', crear_horario, name='formhora'),
    path('horarios/editar/<int:pk>/', editar_horario, name='editar_horario'),
    path('horarios/eliminar/<int:pk>/', eliminar_horario, name='eliminar_horario'),
]
