from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from Otros.models import Horario,Turno,Servicio,Empleado,EstadoTurno, ServiciosXTurno
from .forms import HorarioForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import JsonResponse
from datetime import date
from django.views.decorators.csrf import csrf_exempt


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


def servicios_view(request):
    servicios = Servicio.objects.filter(activo=True)
    return render(request, "reservaserv.html", {"servicios": servicios})

def fechas_view(request):
    horarios = Horario.objects.all().order_by("hora_inicio")
    return render(request, "reservafechas.html", {"horarios": horarios})

def empleados_view(request):
    empleados = Empleado.objects.filter(activo=True, especialidad="barbero")
    return render(request, "reservaemp.html", {"empleados": empleados})

@csrf_exempt
def confirmar_turno(request):
    if request.method == "POST":
        cliente = request.user.cliente
        servicios_ids = request.POST.getlist("servicios[]")
        fecha = request.POST.get("fecha")
        horario_id = request.POST.get("horario")
        empleado_id = request.POST.get("empleado")

        # Crear turno
        estado_pendiente = EstadoTurno.objects.get(nombre="Pendiente")
        turno = Turno.objects.create(
            cliente=cliente,
            empleado_id=empleado_id,
            fecha=fecha,
            horario_id=horario_id,
            estado=estado_pendiente
        )

        # Relacionar servicios
        servicios = Servicio.objects.filter(id__in=servicios_ids)
        duracion_total = 0
        for s in servicios:
            ServiciosXTurno.objects.create(turno=turno, servicio=s)
            duracion_total += s.duracion

        # Guardar duración real
        turno.duracion_real = duracion_total if duracion_total > 0 else 30
        turno.save()

        return JsonResponse({"mensaje": "¡Turno reservado con éxito!"})
    

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def turnos_general(request):
    turnos = Turno.objects.select_related("cliente", "empleado", "estado", "horario")

    data = []
    for t in turnos:
        data.append({
            "fecha": t.fecha.strftime("%d/%m/%Y"),
            "hora": t.horario.hora_inicio.strftime('%H:%M'),
            "cliente": t.cliente.first_name,
            "empleado": t.empleado.user.first_name,
            "estado": t.estado.nombre,
        })

    return render(request, "turnos_general.html", {"turnos": data})