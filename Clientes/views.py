from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import user_passes_test,login_required
from Otros.models import Cliente
from .forms import ClienteAltaForm,ClienteEditarForm


def es_gerente(user):
    return user.groups.filter(name='Gerente').exists() or user.is_superuser

def es_recepcionista(user):
    return user.groups.filter(name='Recepcionista').exists() or es_gerente(user)

@login_required
@user_passes_test(lambda u: es_recepcionista(u))
def lista_clientes(request):
    clientes = Cliente.objects.all()
    # Siempre render completo para la primera carga
    return render(request, 'clientes.html', {'clientes': clientes})

@login_required
@user_passes_test(lambda u: es_recepcionista(u))
def tabla_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes_tabla.html', {'clientes': clientes})



@login_required
@user_passes_test(lambda u: es_recepcionista(u))
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteAltaForm(request.POST)
        if form.is_valid():
            form.save()
            # Enviamos éxito para que el modal se cierre y la tabla se recargue
            return JsonResponse({'success': True})
        else:
            # Enviamos el formulario con errores de validación
            return render(request, 'formcli.html', {'form': form})     
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
            return JsonResponse({'success': True})
        else:
            return render(request, 'formcli.html', {'form': form, 'cliente': cliente})
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
        return JsonResponse({'success': True})
    return render(request, 'eliminarcli.html', {'cliente': cliente})