from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
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
    return render(request, 'clientes.html', {'clientes': clientes})

@login_required
@user_passes_test(lambda u: es_recepcionista(u))
@xframe_options_exempt
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteAltaForm(request.POST)
        if form.is_valid():
            form.save()
            # Avisar al iframe que debe cerrarse:
            return HttpResponse(
                "<script>window.parent.postMessage({action: 'closeBootbox'}, '*');</script>"
            )
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
            return HttpResponse("<script>window.parent.postMessage({action: 'closeBootbox'}, '*');</script>")
    else:
        form = ClienteEditarForm(instance=cliente)
    return render(request, 'formcli.html', {'form': form, 'cliente': cliente})

@login_required
@user_passes_test(es_gerente)
@xframe_options_exempt
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()       # opcional, solo si no se elimina con cascade
        return HttpResponse(
            "<script>window.parent.postMessage({action: 'closeBootbox'}, '*');</script>"
        )
    return render(request, 'eliminarcli.html', {'cliente': cliente})