from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db import transaction
from Otros.models import Venta,Cliente,Servicio, DetalleVenta, Pago, MovimientoStock, MovimientoCaja, MetodoPago,Producto,Caja,ServiciosXTurno,Turno,EstadoTurno
import json
from django.core.serializers.json import DjangoJSONEncoder


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

@login_required
@user_passes_test(es_gerente)
def tabla_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'ventas_tabla.html', {'ventas': ventas})


#=========================================================================
# HACER QUE EL CANCELAR VENTA TAMBIEN CAMBIE EL ESTADO DEL PAGO ASOCIADO A ESA VENTA
# HACER QUE VENTA PUEDA REGISTRAR UN SERVICIO
#=========================================================================

# --- CREAR VENTA ---
@login_required
@user_passes_test(es_gerente)
@transaction.atomic
def crear_venta(request):
    try:
        caja = Caja.objects.get(estado=True)
    except Caja.DoesNotExist:
        return render(request, 'abra_caja.html')
        # return JsonResponse({'error': 'Debe abrir una caja antes de registrar ventas.'})

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        productos = request.POST.getlist('productos[]')
        cantidades = request.POST.getlist('cantidades[]')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        empleado = request.user.empleado

        venta = Venta.objects.create(cliente=cliente, empleado=empleado, caja=caja, total=0)
        total = 0

        for prod_id, cantidad in zip(productos, cantidades):
            if not prod_id or not cantidad:
                continue
            producto = get_object_or_404(Producto, id=prod_id)
            cantidad = int(cantidad)

            if producto.stock_actual < cantidad:
                venta.delete()
                return JsonResponse({'error': f"Stock insuficiente para {producto.nombre}"})

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=producto.precio * cantidad
            )

            producto.stock_actual -= cantidad
            producto.save()

            MovimientoStock.objects.create(
                producto=producto,
                tipo='SALIDA',
                cantidad=cantidad,
                motivo='Venta',
                empleado=empleado,
            )
            total += producto.precio * cantidad

        venta.total = total
        venta.save()

        # En lugar de redirect, devolvemos JSON con la siguiente vista
        return JsonResponse({'next_url': f'/crear/pago/{venta.id}/'})

    context = {
        'productos': Producto.objects.filter(stock_actual__gt=0),
        'clientes': Cliente.objects.filter(activo=True),
    }
    return render(request, 'crear_venta.html', context)

@login_required
@user_passes_test(es_gerente)
@transaction.atomic
def cobrar_turno(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id)

    # Verificar caja abierta
    try:
        caja = Caja.objects.get(estado=True)
    except Caja.DoesNotExist:
        return JsonResponse({'error': 'Debe abrir una caja antes de cobrar un turno.'})

    if request.method == 'POST':
        cliente = turno.cliente
        empleado = request.user.empleado

        # Crear venta base
        venta = Venta.objects.create(cliente=cliente, empleado=empleado, caja=caja, total=0)
        total = 0

        # 1️⃣ Agregar servicios del turno (puede tener varios)
        servicios_turno = ServiciosXTurno.objects.filter(turno=turno, activo=True)
        for st in servicios_turno:
            DetalleVenta.objects.create(
                venta=venta,
                servicio=st.servicio,
                cantidad=1,
                precio_unitario=st.servicio.precio,
                subtotal=st.servicio.precio
            )
            total += st.servicio.precio

        # 2️⃣ Agregar servicios extra si los hay
        servicios_extra = request.POST.getlist('servicios_extra[]')
        servicios_extra = [s for s in servicios_extra if s]
        for serv_id in servicios_extra:
            serv = get_object_or_404(Servicio, id=serv_id)
            DetalleVenta.objects.create(
                venta=venta,
                servicio=serv,
                cantidad=1,
                precio_unitario=serv.precio,
                subtotal=serv.precio
            )
            total += serv.precio

        # 3️⃣ Agregar productos
        productos = request.POST.getlist('productos[]')
        cantidades = request.POST.getlist('cantidades[]')
        for prod_id, cant in zip(productos, cantidades):
            if not prod_id or not cant:
                continue
            producto = get_object_or_404(Producto, id=prod_id)
            cant = int(cant)

            if producto.stock_actual < cant:
                venta.delete()
                return JsonResponse({'error': f"Stock insuficiente para {producto.nombre}"})

            producto.stock_actual -= cant
            producto.save()

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cant,
                precio_unitario=producto.precio,
                subtotal=producto.precio * cant
            )

            MovimientoStock.objects.create(
                producto=producto,
                tipo='SALIDA',
                cantidad=cant,
                motivo=f"Venta producto durante cobro de turno #{turno.id}",
                empleado=empleado,
            )

            total += producto.precio * cant

        # 4️⃣ Actualizar total de la venta
        venta.total = total
        venta.save()

        # 5️⃣ Cambiar estado del turno a "Completado"
        try:
            turno.pagado = True
        except:
            turno.pagado = None  # fallback
        turno.save()

        # 6️⃣ Redirigir al registro de pago
        return JsonResponse({'next_url': f'/crear/pago/{venta.id}/'})

    # GET → Datos para el modal
    servicios_turno_qs = ServiciosXTurno.objects.filter(turno=turno, activo=True)
    context = {
        'turno': turno,
        'servicios_turno': servicios_turno_qs,
        'productos': Producto.objects.filter(activo=True, stock_actual__gt=0),
        'servicios': Servicio.objects.filter(activo=True),
        # ✅ Precios de servicios del turno como lista JSON para JS
        'precios_servicios_json': json.dumps(
            list(servicios_turno_qs.values_list('servicio__precio', flat=True)),
            cls=DjangoJSONEncoder
        ),
        # ✅ IDs de servicios del turno para filtrar en el template
        'servicios_turno_ids': list(servicios_turno_qs.values_list('servicio__id', flat=True)),
        # ✅ Servicios disponibles para agregar (id, nombre, precio)
        'servicios_json': json.dumps(
            list(Servicio.objects.filter(activo=True)
                .values('id', 'nombre', 'precio')),
            cls=DjangoJSONEncoder
        ),
        # ✅ Productos disponibles para agregar (id, nombre, precio, stock_actual)
        'productos_json': json.dumps(
            list(Producto.objects.filter(activo=True, stock_actual__gt=0)
                .values('id', 'nombre', 'precio', 'stock_actual')),
            cls=DjangoJSONEncoder
        ),
    }
    return render(request, 'cobrar_turno.html', context)


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


# --- REGISTRAR PAGO ---
@login_required
@user_passes_test(es_gerente)
@transaction.atomic
def registrar_pago(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    if request.method == 'POST':
        metodos = request.POST.getlist('metodos[]')
        montos = request.POST.getlist('montos[]')

        for metodo_id, monto in zip(metodos, montos):
            if metodo_id and monto and float(monto) > 0:
                Pago.objects.create(
                    venta=venta,
                    metodo_pago_id=metodo_id,
                    monto=float(monto)
                )
                MovimientoCaja.objects.create(
                    caja=venta.caja,
                    tipo='INGRESO',
                    monto=float(monto),
                    descripcion=f"Pago de venta #{venta.id}",
                    empleado=request.user.empleado,
                )
        messages.success(request, "✅ El pago se registro correctamente.")
        return JsonResponse({'success': True})

    context = {
        'venta': venta,
        'metodos_pago': MetodoPago.objects.filter(activo=True),
    }
    return render(request, 'registrar_pago.html', context)




@login_required
@user_passes_test(es_gerente)
@transaction.atomic
def cancelar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    if request.method== 'POST':
        if not venta.activo:
            messages.error(request, f"La venta #{venta.id} ya está cancelada")
            return JsonResponse({'success': True})

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
    return render(request, 'cancelar_venta.html',{'venta': venta})