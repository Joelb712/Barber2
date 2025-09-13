from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Otros.models import Turno, Horario, Servicio, Empleado, EstadoTurno
from django.core.serializers.json import DjangoJSONEncoder
import json
import datetime

# Create your views here.
def Inicio(request):
    # servicios = Servicio.objects.filter(activo=True)
    # empleados = Empleado.objects.filter(activo=True)
    # empleados_list = [
    #     {'id': e.id, 'nombre': e.user.first_name} for e in empleados
    # ]
    # context = {
    #     'servicios_json': json.dumps(list(servicios.values('id','nombre','precio')), cls=DjangoJSONEncoder),
    #     'empleados_json': json.dumps(empleados_list, cls=DjangoJSONEncoder),
    # }
    # return render(request, 'index.html', context)
    return render(request, 'index.html')

@login_required
def dash(request):
    return render(request,'dash.html')

# def catalogo_productos(request):
#     return render(request, 'productos.html')

def contacto(request):
    return render(request,'contacto.html')

def tienda(request):
    return render(request,'tienda.html')

# @login_required
# @csrf_exempt
# def reservar_turno(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)

#             # Relacionar el usuario logueado con el modelo Cliente
#             cliente = request.user.cliente  

#             servicio_id = data.get("servicio_id")
#             empleado_id = data.get("empleado_id")
#             fecha = data.get("fecha")
#             horario_id = data.get("horario_id")

#             turno = Turno.objects.create(
#                 cliente=cliente,
#                 servicio_id=servicio_id,
#                 empleado_id=empleado_id,
#                 fecha=fecha,
#                 horario_id=horario_id,
#                 estado=EstadoTurno.objects.get(nombre="Pendiente")
#             )

#             return JsonResponse({"success": "Turno registrado correctamente", "turno_id": turno.id})
        
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)

#     return JsonResponse({"error": "Método no permitido"}, status=405)

# def horarios_disponibles(request):
#     empleado_id = request.GET.get('empleado')
#     fecha = request.GET.get('fecha')
    
#     if not empleado_id or not fecha:
#         return JsonResponse([], safe=False)

#     turnos_ocupados = Turno.objects.filter(empleado_id=empleado_id, fecha=fecha).values_list('horario_id', flat=True)
    
#     horarios = Horario.objects.exclude(id__in=turnos_ocupados).values('id', 'hora_inicio', 'hora_fin')

#     return JsonResponse(list(horarios), safe=False)