from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now
from Otros.models import Cliente,Turno,EstadoTurno,Empleado,Caja,Pago,Venta,MovimientoCaja
from datetime import date, timedelta
from django.db.models import Sum, Q
from django.http import JsonResponse
from decimal import Decimal

# Create your views here.
def Inicio(request):
    cliente = None
    if request.user.is_authenticated:
        try:
            cliente = Cliente.objects.get(user=request.user)
        except Cliente.DoesNotExist:
            cliente = None
    return render(request, 'index.html', {'cliente': cliente, 'es_index': True})

@login_required
def dash(request):
    try:
        empleadito = Empleado.objects.get(user=request.user)
    except Empleado.DoesNotExist:
        empleadito = None
    return render(request,'dash.html',{'empleadito': empleadito})

def contacto(request):
    cliente = None
    if request.user.is_authenticated:
        try:
            cliente = Cliente.objects.get(user=request.user)
        except Cliente.DoesNotExist:
            cliente = None
    return render(request,'contacto.html',{'cliente': cliente,"es_index": False})

def mis_turnos(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    
    # Estado 'cancelado'
    estado_cancelado = EstadoTurno.objects.get(nombre='cancelado')
    estado_completado = EstadoTurno.objects.get(nombre='completado')
    # Turnos activos: futuros y no cancelados
    turnos_activos = Turno.objects.filter(
        cliente=cliente,
        fecha__gte=date.today()
    ).exclude(estado__in=[estado_cancelado,estado_completado]).order_by('fecha', 'horario__hora_inicio')

    # Historial: turnos pasados o cancelados
    turnos_historial = Turno.objects.filter(cliente=cliente).filter(
        Q(fecha__lt=date.today()) |  
        Q(estado__in=[estado_cancelado, estado_completado]) 
        )
    turnos_historial = turnos_historial.order_by('-fecha', '-horario__hora_inicio')

    return render(request, 'mis_turnos.html', {
        'turnos_activos': turnos_activos,
        'turnos_historial': turnos_historial,
        'cliente': cliente,
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
    messages.success(request, "✅ El turno ha sido cancelado correctamente.")   
    return redirect('mis_turnos')

@login_required
def home_empleado(request):
    empleado = getattr(request.user, 'empleado', None)
    if not empleado:
        return render(request, 'home_sin_empleado.html')
    
    hoy= date.today()
    especialidad = empleado.especialidad

    #--Turnos--
    turnosemp_hoy=  Turno.objects.filter(empleado=empleado, fecha=hoy)
    print("Turnos de hoy:", turnosemp_hoy)
    turnosxempleado= turnosemp_hoy.count()
    completados= turnosemp_hoy.filter(estado__nombre='Completado').count()
    pendientes = turnosemp_hoy.filter(estado__nombre='Pendiente').count()
    cancelados = turnosemp_hoy.filter(estado__nombre='Cancelado').count()

    #Rango de la Semana
    # 📅 Calculamos el rango de fechas de la semana actual
    inicio_semana = hoy
    fin_semana = hoy + timedelta(days=(6 - hoy.weekday()))  # hasta domingo
    # 🔍 Filtramos turnos desde hoy hasta fin de semana
    turnos_semana = Turno.objects.filter(
        empleado=empleado,
        fecha__range=[inicio_semana, fin_semana],
        estado__nombre='Pendiente'
    ).order_by('fecha', 'horario__hora_inicio')

    #turnos de todos
    turnostodos = Turno.objects.filter(fecha=hoy)

    caja = Caja.objects.filter(estado=True).first()  # caja abierta actual
    efectivo = tarjeta = otros = 0
    if caja:
        pagos = Pago.objects.filter(venta__caja=caja, estado=True)

        efectivo = pagos.filter(metodo_pago__nombre__iexact='efectivo').aggregate(total=Sum('monto'))['total'] or 0
        tarjeta = pagos.filter(metodo_pago__nombre__icontains='tarjeta').aggregate(total=Sum('monto'))['total'] or 0
        otros = pagos.exclude(
            Q(metodo_pago__nombre__iexact='efectivo') |
            Q(metodo_pago__nombre__icontains='tarjeta')
        ).aggregate(total=Sum('monto'))['total'] or 0

    total_caja = efectivo + tarjeta + otros

    # Datos gerente
    hoy_local = timezone.localtime(timezone.now()) 

    # 2. Calcular el INICIO del día de hoy (en la zona horaria local)
    # Esto asegura que el replace se haga al inicio del 26 de noviembre (si esa es tu fecha local).
    inicio_hoy_filtro = hoy_local.replace(hour=0, minute=0, second=0, microsecond=0)

    # 3. Calcular el INICIO del día de mañana
    inicio_manana_filtro = inicio_hoy_filtro + timedelta(days=1)

    ventas_del_dia = Venta.objects.filter(
        fecha__gte=inicio_hoy_filtro,
        fecha__lt=inicio_manana_filtro,
        activo=True
    ).aggregate(total_ventas=Sum('total'))

    total_hoy = ventas_del_dia['total_ventas'] or Decimal(0)


    turnos_todos_hoy = Turno.objects.filter(fecha=hoy)

    total_completados_hoy = turnos_todos_hoy.filter(
        estado__nombre__iexact='completado'
    ).count()

    total_pendientes_hoy = turnos_todos_hoy.filter(
        estado__nombre__iexact='pendiente'
    ).count()

    caja_abierta = Caja.objects.filter(estado=True).first()
    
    monto_total_caja = 0.00
    venta_mas_reciente_total = 0.00
    
    if caja_abierta:
        # 1. TOTAL DE INGRESOS POR VENTAS
        ingresos_ventas = Venta.objects.filter(
            activo=True,
            caja=caja_abierta
        ).aggregate(
            total_sum=Sum("total")
        )["total_sum"] or 0

        # 2. TOTAL DE MOVIMIENTOS DE CAJA (Ingresos - Egresos)
        movimientos_caja = MovimientoCaja.objects.filter(
            caja=caja_abierta,
            activo=True
        ).aggregate(
            ingresos=Sum('monto', filter=Q(tipo='INGRESO')),
            egresos=Sum('monto', filter=Q(tipo='EGRESO'))
        )
        
        # Calcular el neto de los movimientos
        neto_movimientos = (movimientos_caja['ingresos'] or 0) - (movimientos_caja['egresos'] or 0)
        
        # 3. MONTO TOTAL DE LA CAJA (Saldo Inicial + Ventas + Movimientos Netos)
        monto_total_caja = caja_abierta.monto_inicial + ingresos_ventas + neto_movimientos
        
        # 4. VENTA MÁS RECIENTE
        try:
            # Filtra las ventas activas de esta caja, ordena por fecha descendente y toma la primera
            venta_reciente = Venta.objects.filter(
                caja=caja_abierta,
                activo=True
            ).latest('fecha')
            
            venta_mas_reciente_total = venta_reciente.total
            
        except Venta.DoesNotExist:
            venta_mas_reciente_total = 0.00 # No hay ventas en esta caja
    else:
        monto_total_caja = 'No hay caja abierta'
        venta_mas_reciente_total = 0.00
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
           # ✅ Caja actual
        'efectivo': efectivo,
        'tarjeta': tarjeta,
        'otros': otros,
        'total_caja': total_caja,
        #gerente
        'total_hoy': total_hoy,
        'total_completados_hoy': total_completados_hoy,
        'total_pendientes_hoy': total_pendientes_hoy,
        'monto_total_caja': monto_total_caja,
        'venta_mas_reciente_total': venta_mas_reciente_total,

    }
    return render(request, 'home.html', context)

@login_required
def mi_perfil(request):
    empleado = get_object_or_404(Empleado, user=request.user)

    if request.method == "POST":
        empleado.user.first_name = request.POST.get("first_name", "")
        empleado.user.last_name = request.POST.get("last_name", "")
        empleado.telefono = request.POST.get("telefono", "")
        empleado.dni = request.POST.get("dni", "")

        if 'foto' in request.FILES:
            empleado.foto = request.FILES['foto']

        email = request.POST.get('email')
        if email and email != empleado.user.email:
            empleado.user.email = email

        empleado.user.save()
        empleado.save()
        messages.success(request, "✅ Tus datos fueron actualizados correctamente.")

        
        return redirect("dash")

    return render(request, "perfil.html", {"empleado": empleado})

def historial_turnos_empleado(request):
    empleado = get_object_or_404(Empleado, user=request.user)

    # Traer TODOS los turnos del empleado
    historial = Turno.objects.filter(
        empleado=empleado
    ).order_by("-fecha", "-horario__hora_inicio")

    # Años disponibles para el selector
    años_disponibles = [
        d.year
        for d in Turno.objects.filter(empleado=empleado).dates('fecha', 'year')
    ]

    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    return render(request, "historial_turnos_empleado.html", {
        "historial": historial,
        "meses": meses,
        "años": años_disponibles,
    })