from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import user_passes_test,login_required
from Otros.models import Cliente,Empleado
from .forms import ClienteAltaForm,ClienteEditarForm


def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.groups.filter(name="Recepcionista").exists() or user.is_superuser

@login_required
@user_passes_test(es_gerente)
def lista_clientes(request):
    empleadito = get_object_or_404(Empleado, user=request.user)
    clientes = Cliente.objects.all()
    # Siempre render completo para la primera carga
    return render(request, 'clientes.html', {'clientes': clientes,'empleadito': empleadito})

@login_required
@user_passes_test(es_gerente)
def tabla_clientes(request):
    empleadito = get_object_or_404(Empleado, user=request.user)
    clientes = Cliente.objects.all()
    return render(request, 'clientes_tabla.html', {'clientes': clientes, 'empleadito': empleadito})



@login_required
@user_passes_test(es_gerente)
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteAltaForm(request.POST)
        if form.is_valid():
            form.save()
            # Enviamos éxito para que el modal se cierre y la tabla se recargue
            return JsonResponse({'success': True,'message': 'Cliente registrado correctamente!'})
        else:
            # Enviamos el formulario con errores de validación
            return render(request, 'formcli.html', {'form': form}, status=400)     
    else:
        form = ClienteAltaForm()
        return render(request, 'formcli.html', {'form': form})


@login_required
@user_passes_test(es_gerente)
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteEditarForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True,'message': 'Datos del cliente actualizados.'})
        else:
            return render(request, 'formcli.html', {'form': form, 'cliente': cliente}, status=400)
    else:
        form = ClienteEditarForm(instance=cliente)
        return render(request, 'formcli.html', {'form': form, 'cliente': cliente})


@login_required
@user_passes_test(es_gerente)
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.activo= False   # borrado logico
        cliente.save()       
        return JsonResponse({'success': True,'message': 'Cliente dado de baja correctamente.'})
    return render(request, 'eliminarcli.html', {'cliente': cliente})