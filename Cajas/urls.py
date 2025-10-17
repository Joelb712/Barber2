from django.urls import path
from . import views

urlpatterns = [
    path("caja/apertura/", views.apertura_caja, name="apertura_caja"),
    path("caja/cierre/", views.cierre_caja, name="cierre_caja"),
    path("cajas/",views.lista_cajas, name="cajas"),
]