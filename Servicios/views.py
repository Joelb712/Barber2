from django.shortcuts import render, get_object_or_404
from Otros.models import Servicio
from .forms import ServicioForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from django.http import JsonResponse


def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.groups.filter(name="Recepcionista").exists() or user.is_superuser

@login_required
@user_passes_test(es_gerente)
def lista_servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'servicios.html', {'servicios': servicios})

@login_required
@user_passes_test(es_gerente)
def tabla_servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'servicios_tabla.html', {'servicios': servicios})

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
