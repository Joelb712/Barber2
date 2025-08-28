from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import RegistroClienteForm


# Create your views here.

def registro_cliente(request):
    form = RegistroClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Cliente registrado correctamente.")
        return redirect('login')  # Ajustá el nombre de tu url de login
    return render(request, 'registration/register.html', {'form': form})
