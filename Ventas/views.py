from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db import transaction
import json
from Otros.models import Venta,Cliente,Servicio, DetalleVenta, Pago, MovimientoStock, MovimientoCaja, MetodoPago,Producto,Caja

# @login_required
# @transaction.atomic
# def crear_venta(request):
#     try:
#         caja = Caja.objects.get(estado=True)
#     except Caja.DoesNotExist:
#         messages.error(request, "No hay una caja abierta. Debe abrir caja primero.")
#         return redirect("apertura_caja")

#     if request.method == 'POST':
#         cliente_id = request.POST.get('cliente')
#         productos_data = request.POST.getlist('productos[]')
#         servicios_data = request.POST.getlist('servicios[]')

#         cliente = get_object_or_404(Cliente, id=cliente_id)
#         empleado = request.user.empleado

#         venta = Venta.objects.create(cliente=cliente, empleado=empleado, caja=caja, total=0)

#         total = 0

#         # Procesar productos
#         for item in productos_data:
#             prod_id, cantidad = item.split('-')
#             producto = get_object_or_404(Producto, id=prod_id)
#             cantidad = int(cantidad)

#             if producto.stock_actual < cantidad:
#                 messages.error(request, f"Stock insuficiente para {producto.nombre}")
#                 venta.delete()
#                 return redirect("crear_venta")

#             DetalleVenta.objects.create(
#                 venta=venta,
#                 producto=producto,
#                 cantidad=cantidad,
#                 precio_unitario=producto.precio,
#                 subtotal=producto.precio * cantidad
#             )

#             # Descontar stock
#             producto.stock_actual -= cantidad
#             producto.save()

#             # Movimiento de stock
#             MovimientoStock.objects.create(
#                 producto=producto,
#                 tipo='SALIDA',
#                 cantidad=cantidad,
#                 motivo='Venta',
#                 empleado=empleado,
#             )

#             total += producto.precio * cantidad

#         # Procesar servicios
#         for serv_id in servicios_data:
#             servicio = get_object_or_404(Servicio, id=serv_id)
#             total += servicio.precio
#             # Podrías guardar DetalleServicio si tuvieras ese modelo

#         # Actualizar total
#         venta.total = total
#         venta.save()

#         # 🚀 En este punto NO registramos pagos todavía
#         # Mandamos a la vista de "registrar pago"
#         return redirect("registrar_pago", venta_id=venta.id)

#     context = {
#         'productos': Producto.objects.filter(stock_actual__gt=0),
#         'servicios': Servicio.objects.all(),
#         'clientes': Cliente.objects.all(),
#     }
#     return render(request, 'crear_venta.html', context)

def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.groups.filter(name="Recepcionista").exists() or user.is_superuser

@login_required
@user_passes_test(es_gerente)
def lista_ventas(request):
    ventas = Venta.objects.all()
    total=0
    for v in ventas:
        if v.activo:
            total += v.total
    return render(request, 'ventas.html', {'ventas': ventas, 'total': total})

def tabla_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'ventas_tabla.html', {'ventas': ventas})


#=========================================================================
# HACER UNA VISTA PARA COBRAR O REGISTRAR PAGO
# CORREGIR LO DE VENTAS, HACER QUE SE ABRA EL MODAL PARA COBRAR LUEGO DE CERRAR EL CREAR VENTA
# EL CANCELAR VENTA NO FUNCIONA DESDE "VENTAS" EL BOTON NO HACE NADA
# HACER QUE VENTA PUEDA REGISTRAR UN SERVICIO
#=========================================================================

@login_required
@transaction.atomic
def crear_venta(request):
    try:
        caja = Caja.objects.get(estado=True)
    except Caja.DoesNotExist:
        messages.error(request, "No hay una caja abierta. Debe abrir caja primero.")
        return JsonResponse({'success': False, 'error': 'No hay una caja abierta. Debe abrir caja primero.'})

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        productos = request.POST.getlist('productos[]')
        cantidades = request.POST.getlist('cantidades[]')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        empleado = request.user.empleado

        venta = Venta.objects.create(cliente=cliente, empleado=empleado, caja=caja, total=0)

        total = 0

        # Procesar productos
        for prod_id, cantidad in zip(productos, cantidades):
            if not prod_id or not cantidad:
                continue

            producto = get_object_or_404(Producto, id=prod_id)
            cantidad = int(cantidad)

            if producto.stock_actual < cantidad:
                messages.error(request, f"Stock insuficiente para {producto.nombre}")
                venta.delete()
                return JsonResponse({'success': False, 'error': f'Stock insuficiente para {producto.nombre}'})

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

        # ✅ Quitamos servicios (solo productos)
        venta.total = total
        venta.save()

        # Mandamos a registrar pago
        return JsonResponse({'success': True, 'venta_id': venta.id})

    context = {
        'productos': Producto.objects.filter(stock_actual__gt=0),
        'clientes': Cliente.objects.all(),
    }
    return render(request, 'crear_venta.html', context)




#@login_required
#@transaction.atomic
# def registrar_pago(request, venta_id):
#     venta = get_object_or_404(Venta, id=venta_id)

#     if request.method == 'POST':
#         pagos_data = request.POST.getlist('pagos[]')

#         for pago_data in pagos_data:
#             metodo_id, monto = pago_data.split('-')
#             Pago.objects.create(
#                 venta=venta,
#                 metodo_pago_id=metodo_id,
#                 monto=float(monto)
#             )

#             # Registrar movimiento en caja
#             MovimientoCaja.objects.create(
#                 caja=venta.caja,
#                 tipo='INGRESO',
#                 monto=float(monto),
#                 descripcion=f"Pago de venta #{venta.id}",
#                 empleado=request.user.empleado,
#             )

#         messages.success(request, f"Venta #{venta.id} cobrada correctamente.")
#         return redirect("lista_ventas")

#     context = {
#         'venta': venta,
#         'metodos_pago': MetodoPago.objects.all(),
#     }
#     return render(request, 'registrar_pago.html', context)


@login_required
@transaction.atomic
def registrar_pago(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    if request.method == 'POST':
        metodos = request.POST.getlist('metodos[]')
        montos = request.POST.getlist('montos[]')

        for metodo_id, monto in zip(metodos, montos):
            if metodo_id and monto and float(monto) > 0:
                # Registrar pago
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
                )

        messages.success(request, f"Venta #{venta.id} cobrada correctamente.")
        return JsonResponse({'success': True})

    context = {
        'venta': venta,
        'metodos_pago': MetodoPago.objects.all(),
    }
    return render(request, 'registrar_pago.html', context)


@login_required
@transaction.atomic
def cancelar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    if request.method== 'POST':
        if not venta.activo:
            return JsonResponse({'success': False, 'error': f'La venta #{venta.id} ya está cancelada.'})

        # Revertir stock
        detalles = DetalleVenta.objects.filter(venta=venta)
        for detalle in detalles:
            producto = detalle.producto
            producto.stock_actual += detalle.cantidad
            producto.save()

            MovimientoStock.objects.create(
                producto=producto,
                tipo='ENTRADA',
                cantidad=detalle.cantidad,
                motivo=f"Cancelación de venta #{venta.id}",
                empleado=request.user.empleado,
            )
            detalle.activo=False
            detalle.save()

        # Movimiento en caja
        MovimientoCaja.objects.create(
            caja=venta.caja,
            tipo='EGRESO',
            monto=venta.total,
            descripcion=f"Cancelación de venta #{venta.id}",
            empleado=request.user.empleado,
        )

        # Marcar venta como inactiva
        venta.activo = False
        venta.save()

        messages.success(request, f"La venta #{venta.id} fue cancelada correctamente.")
        return JsonResponse({'success': True})
    return render(request, 'cancelar_venta.html')