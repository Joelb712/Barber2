from django.urls import path
from . import views

urlpatterns = [
    path("empleados/",views.lista_empleados, name='lista_empleados'),
    path('empleados/tabla/', views.tabla_empleados, name='tabla_empleados'),
    path("empleados/nuevo/", views.crear_empleado, name='formemp'),
    path("empleados/editar/<int:pk>/", views.editar_empleado,name='editar_empleado'),
    path("empleados/eliminar/<int:pk>/", views.eliminar_empleado,name='eliminar_empleado'),
]