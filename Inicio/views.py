from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from Otros.models import Cliente,Turno,EstadoTurno,Empleado,MovimientoCaja,MetodoPago,Caja
from datetime import date, timedelta
from django.db.models import Sum, Q

# Create your views here.
def Inicio(request):
    cliente = None
    if request.user.is_authenticated:
        try:
            cliente = Cliente.objects.get(user=request.user)
        except Cliente.DoesNotExist:
            cliente = None
    return render(request, 'index.html', {'cliente': cliente})

@login_required
def dash(request):
    return render(request,'dash.html')

def contacto(request):
    return render(request,'contacto.html')

def mis_turnos(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    
    # Estado 'cancelado'
    estado_cancelado = EstadoTurno.objects.get(nombre='cancelado')

    # Turnos activos: futuros y no cancelados
    turnos_activos = Turno.objects.filter(
        cliente=cliente,
        fecha__gte=date.today()
    ).exclude(estado=estado_cancelado).order_by('fecha', 'horario__hora_inicio')

    # Historial: turnos pasados o cancelados
    turnos_historial = Turno.objects.filter(
        cliente=cliente
    ).filter(
        fecha__lt=date.today()
    ) | Turno.objects.filter(cliente=cliente, estado=estado_cancelado)

    turnos_historial = turnos_historial.order_by('-fecha', '-horario__hora_inicio')

    return render(request, 'mis_turnos.html', {
        'turnos_activos': turnos_activos,
        'turnos_historial': turnos_historial,
    })

def perfil_cliente(request):
    cliente = get_object_or_404(Cliente, user=request.user)

    if request.method == "POST":
        cliente.first_name = request.POST.get("first_name", "")
        cliente.last_name = request.POST.get("last_name", "")
        cliente.telefono = request.POST.get("telefono", "")
        cliente.dni = request.POST.get("dni", "")
        cliente.notas = request.POST.get("notas", "")
        
        if 'foto' in request.FILES:
            cliente.foto = request.FILES['foto']

        email = request.POST.get('email')
        if email and email != request.user.email:
            request.user.email = email
            request.user.save()

        cliente.save()

        messages.success(request, "✅ Tus datos fueron actualizados correctamente.")
        return redirect("perfil_cliente")

    return render(request, "perfil_cliente.html", {"cliente": cliente})

@login_required
def cancelar_turno(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id, cliente__user=request.user)
    cancelado = EstadoTurno.objects.get(nombre='cancelado')
    turno.estado = cancelado
    turno.save()
    return redirect('mis_turnos')

@login_required
def home_empleado(request):
    empleado = getattr(request.user, 'empleado', None)
    if not empleado:
        return render(request, 'home_sin_empleado.html')
    hoy= date.today()
    especialidad = empleado.especialidad

    turnosemp_hoy=  Turno.objects.filter(empleado=empleado, fecha=hoy)
    print("Turnos de hoy:", turnosemp_hoy)
    turnosxempleado= turnosemp_hoy.count()
    completados= turnosemp_hoy.filter(estado__nombre='Completado').count()
    pendientes = turnosemp_hoy.filter(estado__nombre='Pendiente').count()
    cancelados = turnosemp_hoy.filter(estado__nombre='Cancelado').count()
    # 📅 Calculamos el rango de fechas de la semana actual
    inicio_semana = hoy
    fin_semana = hoy + timedelta(days=(6 - hoy.weekday()))  # hasta domingo

    # 🔍 Filtramos turnos desde hoy hasta fin de semana
    turnos_semana = Turno.objects.filter(
        empleado=empleado,
        fecha__range=[inicio_semana, fin_semana],
        estado__nombre='Pendiente'
    ).order_by('fecha', 'horario__hora_inicio')

    turnostodos = Turno.objects.filter(fecha=hoy)

    context = {
        'empleado': empleado,
        'especialidad': especialidad,
        'cantidad_turnos_hoy': turnosxempleado,
        'turnoshoy':turnosemp_hoy,
        'completados':completados,
        'pendientes': pendientes,
        'cancelados': cancelados,
        'turnos_semana': turnos_semana,
        'inicio_semana': inicio_semana,
        'fin_semana': fin_semana,
        'hoy':hoy,
        'turnostodos':turnostodos,

    }
    return render(request, 'home.html', context)