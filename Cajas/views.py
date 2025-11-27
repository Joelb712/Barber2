from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from Otros.models import Caja, MovimientoCaja, Venta, MetodoPago, Empleado
from .forms import AperturaCajaForm, MetodoForm
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta

# Create your views here.
def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.groups.filter(name="Recepcionista").exists() or user.is_superuser


@login_required
@user_passes_test(es_gerente)
def lista_cajas(request):
    empleadito = get_object_or_404(Empleado, user=request.user)
    hoy = now()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # INGRESOS
    ingresos_semanal = Venta.objects.filter(
        activo=True,
        fecha__gte=inicio_semana
    ).aggregate(total=Sum("total"))["total"] or 0

    ingresos_mensual = Venta.objects.filter(
        activo=True,
        fecha__gte=inicio_mes
    ).aggregate(total=Sum("total"))["total"] or 0

    caja_abierta = Caja.objects.filter(estado=True).first()
    if caja_abierta:
        ingresos_caja_actual = (
            Venta.objects.filter(
                activo=True,
                caja=caja_abierta
            ).aggregate(total=Sum("total"))["total"] or 0
        )
    else:
        ingresos_caja_actual = "No hay caja abierta"


    cajas= Caja.objects.all()
    return render(request, 'cajas.html', {'cajas': cajas, 'empleadito': empleadito,'ingresos_semanal': ingresos_semanal,
        'ingresos_mensual': ingresos_mensual,
        'ingresos_caja_actual': ingresos_caja_actual,})

@login_required
@user_passes_test(es_gerente)
def tabla_cajas(request):
    empleadito = get_object_or_404(Empleado, user=request.user)
    cajas = Caja.objects.all()
    return render(request, 'cajas_tabla.html', {'cajas': cajas,'empleadito': empleadito})


@login_required
def apertura_caja(request):
    """Muestra modal de apertura o mensaje si ya hay caja abierta"""
    caja_abierta = Caja.objects.filter(estado=True).exists()

    if request.method == 'GET':
        if caja_abierta:
            # --- CODIGO ORIGINAL COMENTADO (NO SIRVE PARA EL MODAL GENERICO) ---
            # html = render_to_string('caja_abierta.html', {}, request=request)
            # return JsonResponse({'html': html})
            # -------------------------------------------------------------------
            return render(request, 'caja_abierta.html')

        # --- CODIGO ORIGINAL COMENTADO ---
        # form = AperturaCajaForm()
        # html = render_to_string('apertura_caja.html', {'form': form}, request=request)
        # return JsonResponse({'html': html})
        # ----------------------------------
        form = AperturaCajaForm()
        return render(request, 'apertura_caja.html', {'form': form})

    # Si viene un POST, procesamos el formulario
    elif request.method == 'POST':
        form = AperturaCajaForm(request.POST)
        if form.is_valid():
            
            # Validación extra por seguridad
            if caja_abierta:
                 return JsonResponse({'success': False, 'message': 'Ya existe una caja abierta.'}, status=400)
            
            if not hasattr(request.user, 'empleado'):
                 return JsonResponse({'success': False, 'message': 'Usuario no es empleado.'}, status=403)

            monto_inicial = form.cleaned_data['monto_inicial']
            empleado = request.user.empleado

            Caja.objects.create(
                empleado=empleado,
                monto_inicial=monto_inicial,
                estado=True
            )
            return JsonResponse({'success': True, 'message': 'Caja abierta correctamente'})
        else:
            # --- CODIGO ORIGINAL COMENTADO ---
            # html = render_to_string('apertura_caja.html', {'form': form}, request=request)
            # return JsonResponse({'html': html, 'success': False})
            # ----------------------------------
            
            # Devolvemos HTML directo (con status 400 opcional) para que se vea dentro del modal
            return render(request, 'apertura_caja.html', {'form': form}, status=400)


@login_required
def cierre_caja(request):
    """Muestra modal para cerrar caja o mensaje si no hay ninguna abierta"""
    if request.method == 'GET':
        try:
            caja = Caja.objects.get(estado=True)
            # --- CODIGO ORIGINAL COMENTADO ---
            # html = render_to_string('cierre.html', {'caja': caja}, request=request)
            # return JsonResponse({'html': html})
            # ----------------------------------
            return render(request, 'cierre.html', {'caja': caja})
        except Caja.DoesNotExist:
            # --- CODIGO ORIGINAL COMENTADO ---
            # html = render_to_string('sin_caja.html', {}, request=request)
            # return JsonResponse({'html': html})
            # ----------------------------------
            return render(request, 'sin_caja.html')

    elif request.method == 'POST':
        try:
            caja = Caja.objects.get(estado=True)
            total_ventas = Venta.objects.filter(caja=caja).aggregate(total=models.Sum("total"))["total"] or 0
            
            # Lógica de cierre
            caja.monto_final = caja.monto_inicial + total_ventas
            caja.fecha_cierre = timezone.now()
            caja.estado = False
            caja.save()
            return JsonResponse({'success': True, 'message': 'Caja cerrada correctamente'})
        except Caja.DoesNotExist:
            return JsonResponse({'error': 'No hay ninguna caja abierta'}, status=400)
        
@login_required
@user_passes_test(es_gerente)
def lista_metodos(request):
    metodos = MetodoPago.objects.all()
    # Siempre render completo para la primera carga
    return render(request, 'metodospago.html', {'metodos': metodos})

@login_required
@user_passes_test(es_gerente)
def tabla_metodos(request):
    metodos = MetodoPago.objects.all()
    return render(request, 'metodos_tabla.html', {'metodos': metodos})



@login_required
@user_passes_test(es_gerente)
def crear_metodo(request):
    if request.method == 'POST':
        form = MetodoForm(request.POST)
        if form.is_valid():
            form.save()
            # Enviamos éxito para que el modal se cierre y la tabla se recargue
            return JsonResponse({'success': True, 'message': 'Método de pago agregado correctamente'})
        else:
            # Enviamos el formulario con errores de validación
            return render(request, 'formMetodo.html', {'form': form})     
    else:
        form = MetodoForm()
        return render(request, 'formMetodo.html', {'form': form})


@login_required
@user_passes_test(es_gerente)
def estado_metodo(request, pk):
    metodo = get_object_or_404(MetodoPago, pk=pk)
    if metodo.activo == False:
        if request.method == 'POST':
            metodo.activo = True # activado
            metodo.save()
            return JsonResponse({'success': True, 'message':'Método de pago habilitado correctamente'})
    else:
        if request.method == 'POST':
            metodo.activo= False   # desactivado
            metodo.save()       
            return JsonResponse({'success': True, 'message':'Método de pago deshabilitado correctamente'})
    return render(request, 'estadometodo.html', {'metodo': metodo})

@login_required
@user_passes_test(es_gerente)
def ventas_de_caja(request, pk):
    caja = get_object_or_404(Caja, pk=pk)
    ventas = Venta.objects.filter(caja=caja, activo=True)
    return render(request, 'ventasdecaja.html', {'caja': caja, 'ventas': ventas})