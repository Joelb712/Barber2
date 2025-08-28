from django.urls import path
from . import views

urlpatterns = [
    path("clientes/",views.lista_clientes, name='lista_clientes'),
    path("clientes/nuevo/", views.crear_cliente, name='formcli'),
    path("clientes/editar/<int:pk>/", views.editar_cliente,name='editar_cliente'),
    path("clientes/eliminar/<int:pk>/", views.eliminar_cliente,name='eliminar_cliente'),

]