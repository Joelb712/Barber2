from django.urls import path
from . import views

urlpatterns = [
    path("ventas",views.lista_ventas, name='lista_ventas'),
    path('crear/', views.crear_venta, name="crear_venta"),
    path('pago/<int:venta_id>/', views.registrar_pago, name="registrar_pago"),
]