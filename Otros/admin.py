from django.contrib import admin
from Otros.models import Cliente, Empleado, Producto, Servicio, Horario, Turno, EstadoTurno, ServiciosXTurno

# Register your models here.

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'telefono', 'dni', 'activo', 'fecha_registro')
    search_fields = ('first_name', 'last_name', 'user__username', 'dni')
    list_filter = ('activo', 'fecha_registro')
    ordering = ('-fecha_registro',)
@admin.register(Empleado)

class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'telefono', 'dni', 'especialidad', 'activo', 'fecha_registro')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'dni')
    list_filter = ('especialidad', 'activo', 'fecha_registro')
    ordering = ('-fecha_registro',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock_actual', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)
    ordering = ('nombre',)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)
    ordering = ('nombre',)

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('hora_inicio', 'hora_fin')
    search_fields = ('hora_inicio', 'hora_fin')
    ordering = ('hora_inicio',)

@admin.register(EstadoTurno)
class EstadoTurnoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'empleado', 'fecha', 'horario', 'estado')
    list_filter = ('estado', 'fecha')

@admin.register(ServiciosXTurno)
class ServiciosXTurnoAdmin(admin.ModelAdmin):
    list_display = ('turno', 'servicio')
    search_fields = ('turno__cliente__user__username', 'servicio__nombre')
    ordering = ('turno', 'servicio')
