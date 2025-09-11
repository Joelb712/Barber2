from django.urls import path
from .views import *

urlpatterns = [
    path('servicios/', lista_servicios, name='lista_servicios'),
    path('servicios/nuevo/', crear_servicio, name='formserv'),
    path('servicios/editar/<int:pk>/', editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<int:pk>/', eliminar_servicio, name='eliminar_servicio'),
]
