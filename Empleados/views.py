from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import user_passes_test,login_required
from Otros.models import Empleado
from Usuarios.forms import EmpleadoCreateForm,EmpleadoEditarForm


def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.groups.filter(name="Recepcionista").exists() or user.is_superuser

@login_required
@user_passes_test(es_gerente)
def lista_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'empleados.html', {'empleados': empleados})


@login_required
@user_passes_test(es_gerente)
def tabla_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'empleados_tabla.html', {'empleados': empleados})


@login_required
@user_passes_test(es_gerente)
def crear_empleado(request):
    if request.method == 'POST':
        print("FILES:", request.FILES)
        form = EmpleadoCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Enviamos éxito para que el modal se cierre y la tabla se recargue
            return JsonResponse({'success': True})
        else:
            # Enviamos el formulario con errores de validación
            return render(request, 'formemp.html', {'form': form}) 
    else:
        form = EmpleadoCreateForm()
        return render(request, 'formemp.html', {'form': form})


@login_required
@user_passes_test(es_gerente)
def editar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoEditarForm(request.POST,request.FILES, instance=empleado, user_instance=empleado.user)
        if form.is_valid():
            form.save()
             # Avisar al iframe que debe cerrarse:
            return JsonResponse({'success': True})
        else:
            return render(request, 'formemp.html', {'form': form, 'empleado': empleado})
    else:
        form = EmpleadoEditarForm(instance=empleado, user_instance=empleado.user)
        return render(request,('formemp.html'),{'form':form , 'empleado':empleado})


@login_required
@user_passes_test(es_gerente)
def eliminar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.activo= False
        empleado.save()
        return JsonResponse({'success': True})
    return render(request, 'eliminaremp.html', {'empleado': empleado})