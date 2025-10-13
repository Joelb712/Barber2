from django.urls import path
from . import views

urlpatterns = [
    path("ventas",views.lista_ventas, name='lista_ventas'),
    path('crear/', views.crear_venta, name="crear_venta"),
    path('crear/pago/<int:venta_id>/', views.registrar_pago, name="registrar_pago"),
    path('ventas/cancelar/<int:venta_id>/', views.cancelar_venta, name="cancelar_venta"),
]