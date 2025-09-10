from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import user_passes_test,login_required
from Otros.models import Empleado
from Usuarios.forms import EmpleadoCreateForm,EmpleadoEditarForm




def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.is_superuser

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def lista_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'empleados.html', {'empleados': empleados})

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def crear_empleado(request):
    if request.method == 'POST':
        form = EmpleadoCreateForm(request.POST)
        if form.is_valid():
            form.save()
            # Avisar al iframe que debe cerrarse:
            return HttpResponse(
                "<script>window.parent.postMessage({action: 'closeBootbox'}, '*');</script>"
            )
    else:
        form = EmpleadoCreateForm()
    
    return render(request, 'formemp.html', {'form': form})

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def editar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoEditarForm(request.POST, instance=empleado, user_instance=empleado.user)
        if form.is_valid():
            form.save()
             # Avisar al iframe que debe cerrarse:
            return HttpResponse(
                "<script>window.parent.postMessage({action: 'closeBootbox'}, '*');</script>"
            )
    else:
        form = EmpleadoEditarForm(instance=empleado, user_instance=empleado.user)
    return render(request,('formemp.html'),{'form':form , 'Empleado':empleado})

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def eliminar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.user.delete()  # elimina también el User relacionado
        empleado.delete()       # opcional, solo si no se elimina con cascade
        return HttpResponse(
            "<script>window.parent.postMessage({action: 'closeBootbox'}, '*');</script>"
        )
    return render(request, 'eliminaremp.html', {'empleado': empleado})