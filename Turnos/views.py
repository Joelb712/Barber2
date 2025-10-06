from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from Otros.models import Horario,Turno,Servicio,Empleado,EstadoTurno, ServiciosXTurno,Cliente
from .forms import HorarioForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date
import json

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


# def servicios_view(request):
#     servicios = Servicio.objects.filter(activo=True)
#     return render(request, "reservaserv.html", {"servicios": servicios})

# def fechas_view(request):
#     horarios = Horario.objects.all().order_by("hora_inicio")
#     return render(request, "reservafechas.html", {"horarios": horarios})

# def empleados_view(request):
#     empleados = Empleado.objects.filter(activo=True, especialidad="barbero")
#     return render(request, "reservaemp.html", {"empleados": empleados})

# @csrf_exempt
# def confirmar_turno(request):
#     if request.method == "POST":
#         cliente = request.user.cliente
#         servicios_ids = request.POST.getlist("servicios[]")
#         fecha = request.POST.get("fecha")
#         horario_id = request.POST.get("horario")
#         empleado_id = request.POST.get("empleado")

#         # Crear turno
#         estado_pendiente = EstadoTurno.objects.get(nombre="Pendiente")
#         turno = Turno.objects.create(
#             cliente=cliente,
#             empleado_id=empleado_id,
#             fecha=fecha,
#             horario_id=horario_id,
#             estado=estado_pendiente
#         )

#         # Relacionar servicios
#         servicios = Servicio.objects.filter(id__in=servicios_ids)
#         duracion_total = 0
#         for s in servicios:
#             ServiciosXTurno.objects.create(turno=turno, servicio=s)
#             duracion_total += s.duracion

#         # Guardar duración real
#         turno.duracion_real = duracion_total if duracion_total > 0 else 30
#         turno.save()

#         return JsonResponse({"mensaje": "¡Turno reservado con éxito!"})
    

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
            "empleado": t.empleado.user.first_name if t.empleado else "No asignado",
            "estado": t.estado.nombre,
        })

    return render(request, "turnos_general.html", {"turnos": data})


# def horarios_disponibles(request):
#     empleado_id = request.GET.get('empleado_id')
#     fecha = request.GET.get('fecha')

#     if not empleado_id or not fecha:
#         return JsonResponse({"error": "Faltan parámetros"}, status=400)

#     try:
#         fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
#     except ValueError:
#         return JsonResponse({"error": "Formato de fecha inválido"}, status=400)

#     horarios = Horario.objects.all()

#     # Excluir horarios que ya estén ocupados por ese empleado en esa fecha
#     ocupados = Turno.objects.filter(empleado_id=empleado_id, fecha=fecha_obj).values_list('horario_id', flat=True)
#     disponibles = horarios.exclude(id__in=ocupados)

#     data = [{"id": h.id, "hora": h.hora_inicio.strftime("%H:%M")} for h in disponibles]
#     return JsonResponse(data, safe=False)

# def horarios_disponibles(request):
#     empleado_id = request.GET.get("empleado_id")
#     fecha = request.GET.get("fecha")
    
#     if not empleado_id or not fecha:
#         return JsonResponse({"error": "Faltan datos"}, status=400)
    
#     # Obtener todos los horarios
#     todos = Horario.objects.all()
    
#     # Obtener horarios ocupados para ese empleado en esa fecha
#     ocupados = Turno.objects.filter(
#         empleado_id=empleado_id,
#         fecha=fecha
#     ).values_list("horario_id", flat=True)
    
#     # Filtrar los horarios disponibles
#     disponibles = todos.exclude(id__in=ocupados)
    
#     # Preparar respuesta
#     data = [{"id": h.id, "hora": h.hora_inicio.strftime("%H:%M")} for h in disponibles]
#     return JsonResponse(data, safe=False)

@login_required
# def solicitar_turno(request):
#     """Vista que renderiza la página desde donde se abre el modal"""
#     return render(request, 'solicitar_turno.html')

def get_servicios(request):
    servicios = Servicio.objects.filter(activo=True).values('id', 'nombre','descripcion', 'duracion', 'precio')
    return JsonResponse(list(servicios), safe=False)

def get_barberos(request):
    barberos = Empleado.objects.filter(
        activo=True,
        especialidad='barbero'
    ).select_related('user').values(
        'id', 'user__first_name', 'user__last_name'
    )
    return JsonResponse([
        {
            'id': b['id'],
            'nombre': f"{b['user__first_name']} {b['user__last_name']}"
        } for b in barberos
    ], safe=False)

def get_horarios_disponibles(request):
    empleado_id = request.GET.get('empleado_id')
    fecha_str = request.GET.get('fecha')
    
    if not empleado_id or not fecha_str:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)
    
    try:
        fecha = parse_date(fecha_str)
    except:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)

    # Todos los horarios posibles
    todos_horarios = Horario.objects.all()
    
    # Horarios ya ocupados para ese empleado y fecha
    ocupados = Turno.objects.filter(
        empleado_id=empleado_id,
        fecha=fecha
    ).values_list('horario_id', flat=True)
    
    disponibles = [
        {'id': h.id, 'hora': h.hora_inicio.strftime('%H:%M')}
        for h in todos_horarios if h.id not in ocupados
    ]
    
    return JsonResponse(disponibles, safe=False)

@csrf_exempt
@login_required
def crear_turno(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        servicio_ids = data.get('servicios', [])
        empleado_id = data.get('empleado_id')
        fecha_str = data.get('fecha')
        horario_id = data.get('horario_id')
        
        if not (servicio_ids and empleado_id and fecha_str and horario_id):
            return JsonResponse({'error': 'Faltan datos'}, status=400)
        
        fecha = parse_date(fecha_str)
        
        # Validar que el horario esté disponible
        if Turno.objects.filter(
            empleado_id=empleado_id,
            fecha=fecha,
            horario_id=horario_id
        ).exists():
            return JsonResponse({'error': 'Horario no disponible'}, status=400)
        
        # Obtener o crear cliente
        cliente, _ = Cliente.objects.get_or_create(
            user=request.user,
            defaults={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        )
        
        # Estado "pendiente"
        estado_pendiente = EstadoTurno.objects.get(nombre='pendiente')
        
        # Crear turno
        turno = Turno.objects.create(
            cliente=cliente,
            empleado_id=empleado_id,
            fecha=fecha,
            horario_id=horario_id,
            estado=estado_pendiente
        )
        
        # Relacionar servicios
        for sid in servicio_ids:
            ServiciosXTurno.objects.create(turno=turno, servicio_id=sid)
        
        return JsonResponse({'success': True, 'turno_id': turno.id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)