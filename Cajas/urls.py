from django.urls import path
from . import views

urlpatterns = [
    path("caja/apertura/", views.apertura_caja, name="apertura_caja"),
    path("caja/cierre/", views.cierre_caja, name="cierre_caja"),
    path("cajas/",views.lista_cajas, name="cajas"),
    path('cajas/tabla/', views.tabla_cajas, name='tabla_cajas'),
    path("metodos/",views.lista_metodos, name="metodos"),
    path('metodos/tabla/', views.tabla_metodos, name='tabla_metodos'),
    path("metodos/nuevo/", views.crear_metodo, name="crear_metodo"),
    path("metodos/estado/<int:pk>/", views.estado_metodo, name="estado_metodo"),
    path('ventasdecaja/<int:pk>/', views.ventas_de_caja, name='ventas_de_caja'),
]