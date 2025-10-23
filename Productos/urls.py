from django.urls import path
from .views import *

urlpatterns = [
    path('productos/', lista_productos, name='lista_productos'),
    path('productos/tabla/', tabla_productos, name='tabla_productos'),
    path('productos/nuevo/', crear_producto, name='formprod'),
    path('productos/editar/<int:pk>/', editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', eliminar_producto, name='eliminar_producto'),
    path('api/productos/', get_productos, name='get_productos'),
]
