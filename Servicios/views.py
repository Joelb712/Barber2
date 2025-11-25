from django.shortcuts import render, get_object_or_404
from Otros.models import Servicio, Empleado, DetalleVenta
from .forms import ServicioForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils.timezone import now
from datetime import timedelta

def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.groups.filter(name="Recepcionista").exists() or user.is_superuser

@login_required
@user_passes_test(es_gerente)
def lista_servicios(request):
    empleadito = get_object_or_404(Empleado, user=request.user)
    servicios = Servicio.objects.all()

    servicios_disponibles = Servicio.objects.filter(activo=True).count()

    # Fechas
    hoy = now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 2) Servicio más solicitado del mes
    servicio_mas_solicitado = (
        DetalleVenta.objects.filter(
            activo=True,
            servicio__isnull=False,
            venta__activo=True,
            venta__fecha__gte=inicio_mes
        )
        .values("servicio__nombre")
        .annotate(total_solicitudes=Sum("cantidad"))
        .order_by("-total_solicitudes")
        .first()
    )
    if servicio_mas_solicitado:
        nombre_servicio_mas_solicitado = servicio_mas_solicitado["servicio__nombre"]
        cantidad_servicio_mas_solicitado = servicio_mas_solicitado["total_solicitudes"]
    else:
        nombre_servicio_mas_solicitado = "Sin datos"
        cantidad_servicio_mas_solicitado = 0

    # 3) Servicios inactivos
    servicios_inactivos = Servicio.objects.filter(activo=False).count()

    return render(request, 'servicios.html', {'servicios': servicios, 'empleadito': empleadito,"servicios_disponibles": servicios_disponibles,
        "nombre_servicio_mas_solicitado": nombre_servicio_mas_solicitado,
        "cantidad_servicio_mas_solicitado": cantidad_servicio_mas_solicitado,
        "servicios_inactivos": servicios_inactivos,})

@login_required
@user_passes_test(es_gerente)
def tabla_servicios(request):
    empleadito = get_object_or_404(Empleado, user=request.user)
    servicios = Servicio.objects.all()
    return render(request, 'servicios_tabla.html', {'servicios': servicios, 'empleadito': empleadito})

@login_required
@user_passes_test(es_gerente)
def crear_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            # Avisar al iframe que debe cerrarse:
            return JsonResponse({'success': True})
        else:
            return render(request, 'formserv.html', {'form': form})
    else:
        form = ServicioForm()
        return render(request, 'formserv.html', {'form': form})

@login_required
@user_passes_test(es_gerente)
def editar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado correctamente.')
            return JsonResponse({'success': True})
        else:
            return render(request, 'formserv.html', {'form': form, 'servicio': servicio})
    else:
        form = ServicioForm(instance=servicio)
        return render(request, 'formserv.html', {'form': form, 'servicio': servicio})

@login_required
@user_passes_test(es_gerente)
def eliminar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        servicio.activo = False
        servicio.save()
        messages.success(request, 'Servicio eliminado correctamente.')
        return JsonResponse({'success': True})
    return render(request, 'eliminarserv.html', {'servicio': servicio})
