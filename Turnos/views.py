from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from Otros.models import Horario,Turno,Servicio,Empleado,EstadoTurno
from .forms import HorarioForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import JsonResponse


def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.is_superuser

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def lista_horarios(request):
    horarios = Horario.objects.all()
    return render(request, 'horarios.html', {'horarios': horarios})

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def crear_horario(request):
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            form.save()
            # Avisar al iframe que debe cerrarse:
            return HttpResponse(
                "<script>window.parent.postMessage({action: 'closeBootbox'}, '*');</script>"
            )
    else:
        form = HorarioForm()
    return render(request, 'formhora.html', {'form': form})

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def editar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        form = HorarioForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Horario actualizado correctamente.')
            return HttpResponse(
                "<script>window.parent.postMessage({action: 'closeBootbox'}, '*');</script>"
            )
    else:
        form = HorarioForm(instance=horario)
    return render(request, 'formhora.html', {'form': form, 'titulo': 'Editar Horario'})

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def eliminar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        horario.delete()
        messages.success(request, 'Horario eliminado correctamente.')
        return HttpResponse(
            "<script>window.parent.postMessage({action: 'closeBootbox'}, '*');</script>"
        )
    return render(request, 'eliminarhora.html', {'objeto': horario, 'tipo': 'Horario'})


