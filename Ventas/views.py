from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
import json
from Otros.models import Venta,Cliente,Servicio, DetalleVenta, Pago, MovimientoStock, MovimientoCaja, MetodoPago,Producto,Caja

@login_required
@transaction.atomic
def crear_venta(request):
    try:
        caja = Caja.objects.get(estado=True)
    except Caja.DoesNotExist:
        messages.error(request, "No hay una caja abierta. Debe abrir caja primero.")
        return redirect("apertura_caja")

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        productos_data = request.POST.getlist('productos[]')
        servicios_data = request.POST.getlist('servicios[]')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        empleado = request.user.empleado

        venta = Venta.objects.create(cliente=cliente, empleado=empleado, caja=caja, total=0)

        total = 0

        # Procesar productos
        for item in productos_data:
            prod_id, cantidad = item.split('-')
            producto = get_object_or_404(Producto, id=prod_id)
            cantidad = int(cantidad)

            if producto.stock_actual < cantidad:
                messages.error(request, f"Stock insuficiente para {producto.nombre}")
                venta.delete()
                return redirect("crear_venta")

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=producto.precio * cantidad
            )

            # Descontar stock
            producto.stock_actual -= cantidad
            producto.save()

            # Movimiento de stock
            MovimientoStock.objects.create(
                producto=producto,
                tipo='SALIDA',
                cantidad=cantidad,
                motivo='Venta',
                empleado=empleado,
            )

            total += producto.precio * cantidad

        # Procesar servicios
        for serv_id in servicios_data:
            servicio = get_object_or_404(Servicio, id=serv_id)
            total += servicio.precio
            # Podrías guardar DetalleServicio si tuvieras ese modelo

        # Actualizar total
        venta.total = total
        venta.save()

        # 🚀 En este punto NO registramos pagos todavía
        # Mandamos a la vista de "registrar pago"
        return redirect("registrar_pago", venta_id=venta.id)

    context = {
        'productos': Producto.objects.filter(stock_actual__gt=0),
        'servicios': Servicio.objects.all(),
        'clientes': Cliente.objects.all(),
    }
    return render(request, 'crear_venta.html', context)

# Create your views here.

@login_required
@transaction.atomic
def registrar_pago(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    if request.method == 'POST':
        pagos_data = request.POST.getlist('pagos[]')

        for pago_data in pagos_data:
            metodo_id, monto = pago_data.split('-')
            Pago.objects.create(
                venta=venta,
                metodo_pago_id=metodo_id,
                monto=float(monto)
            )

            # Registrar movimiento en caja
            MovimientoCaja.objects.create(
                caja=venta.caja,
                tipo='INGRESO',
                monto=float(monto),
                descripcion=f"Pago de venta #{venta.id}",
                empleado=request.user.empleado,
                venta=venta
            )

        messages.success(request, f"Venta #{venta.id} cobrada correctamente.")
        return redirect("lista_ventas")

    context = {
        'venta': venta,
        'metodos_pago': MetodoPago.objects.all(),
    }
    return render(request, 'registrar_pago.html', context)

@login_required
@xframe_options_exempt
def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'ventas.html', {'ventas': ventas})