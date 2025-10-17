from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Otros.models import Caja, MovimientoCaja, Venta
from .forms import AperturaCajaForm
from django.contrib import messages
from django.db import models

# Create your views here.
@login_required
def apertura_caja(request):
    if Caja.objects.filter(estado=True).exists():
        # ya hay una caja abierta
        return render(request, "caja_abierta.html")

    if request.method == "POST":
        form = AperturaCajaForm(request.POST)
        if form.is_valid():
            monto_inicial = form.cleaned_data["monto_inicial"]
            empleado = request.user.empleado  # o como relaciones tu modelo

            Caja.objects.create(
                empleado=empleado,
                monto_inicial=monto_inicial,
                estado=True
            )
            return redirect("cajas")  # donde quieras redirigir
    else:
        form = AperturaCajaForm()

    return render(request, "apertura_caja.html", {"form": form})

@login_required
def cierre_caja(request):
    try:
        caja = Caja.objects.get(estado=True)
    except Caja.DoesNotExist:
        messages.error(request, "No hay ninguna caja abierta.")
        return redirect("vista.html")

    if request.method == "POST":
        # calcular total ventas de esta caja
        total_ventas = Venta.objects.filter(caja=caja).aggregate(total=models.Sum("total"))["total"] or 0
        caja.monto_final = caja.monto_inicial + total_ventas
        caja.fecha_cierre = timezone.now()
        caja.estado = False
        caja.save()

        messages.success(request, f"Caja cerrada. Total final: ${caja.monto_final}")
        return redirect("cajas")

    return render(request, "cierre.html", {"caja": caja})


def lista_cajas(request):
    cajas= Caja.objects.all()
    return render(request, 'cajas.html', {'cajas': cajas})