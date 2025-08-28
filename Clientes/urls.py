from django.urls import path
from . import views

urlpatterns = [
    path("clientes/",views.lista_clientes, name='lista_clientes'),
    path("clientes/nuevo/", views.crear_cliente, name='formcli'),
]