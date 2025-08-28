from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import user_passes_test,login_required
from Otros.models import Cliente
from .forms import ClienteAltaForm
from Usuarios.forms import EmpleadoCreateForm


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