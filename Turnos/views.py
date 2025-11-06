from django.shortcuts import render, get_object_or_404,HttpResponse
from Otros.models import Horario,Turno,Servicio,Empleado,EstadoTurno, ServiciosXTurno,Cliente
from .forms import HorarioForm, TurnoForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date
import json

def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.groups.filter(name="Recepcionista").exists() or user.is_superuser

@login_required
@user_passes_test(es_gerente)
def lista_horarios(request):
    horarios = Horario.objects.all()
    return render(request, 'horarios.html', {'horarios': horarios})

@login_required
@user_passes_test(es_gerente)
def tabla_horarios(request):
    horarios = Horario.objects.all()
    return render(request, 'horarios_tabla.html', {'horarios': horarios})

@login_required
@user_passes_test(es_gerente)
def crear_horario(request):
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            # Enviamos el formulario con errores de validación
            return render(request, 'formhora.html', {'form': form})  
    else:
        form = HorarioForm()
        return render(request, 'formhora.html', {'form': form})

@login_required
@user_passes_test(es_gerente)
def editar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        form = HorarioForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return render(request, 'formhora.html', {'form': form, 'horarios': horario})
    else:  
        form = HorarioForm(instance=horario)
        return render(request, 'formhora.html', {'form': form, 'horarios': horario})

@login_required
@user_passes_test(es_gerente)
def eliminar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        horario.activo=False
        horario.save()
        # horario.delete()
        return JsonResponse({'success': True})
    return render(request, 'eliminarhora.html', {'horario':horario})


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
    

@login_required
@user_passes_test(es_gerente)
def turnos_general(request):
    turnos = Turno.objects.all()
    return render(request, 'turnos_general.html', {'turnos': turnos})

@login_required
@user_passes_test(es_gerente)
def tabla_turnos(request):
    turnos = Turno.objects.all()
    return render(request, 'turnos_tabla.html', {'turnos': turnos})


@login_required
@user_passes_test(es_gerente)
def dar_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            # Enviamos el formulario con errores de validación
            return render(request, 'formturno.html', {'form': form})  
    else:
        form= TurnoForm()
        return render(request, 'formturno.html', {'form': form})


@login_required
@user_passes_test(es_gerente)
def editar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return render(request, 'formturno.html', {'form': form, 'turno': turno})
    else:
        form = TurnoForm(instance=turno)
        return render(request,('formturno.html'),{'form':form , 'turno':turno})


@login_required
@user_passes_test(es_gerente)
def eliminar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    cancelado = EstadoTurno.objects.get(nombre='cancelado')
    if request.method == 'POST':
        turno.estado = cancelado
        turno.save()
        return JsonResponse({'success': True})
    return render(request, 'eliminarturno.html', {'turno': turno})