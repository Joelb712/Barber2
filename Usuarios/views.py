from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import RegistroClienteForm, LoginUsuarioForm
from django.urls import reverse
from Otros.models import Empleado
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def login_personalizado(request):
    if request.method == 'POST':
        # Instanciar el formulario con los datos enviados
        form = LoginUsuarioForm(request, data=request.POST)
        if form.is_valid():
            # Obtener el nombre de usuario y la contraseña del formulario
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Autenticar al usuario
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Iniciar sesión si el usuario es válido
                login(request, user)
                try:
                    empleado = Empleado.objects.get(user=user)
                    # Si existe, redirigir al dashboard
                    return redirect('dash')
                except Empleado.DoesNotExist:
                    # Si no está vinculado, redirigir al inicio general
                    return redirect('Inicio')
            else:
                # Si la autenticación falla, añadir un error al formulario
                form.add_error(None, 'Nombre de usuario o contraseña incorrectos.')
    else:
        # Si la solicitud es GET, mostrar un formulario vacío
        form = LoginUsuarioForm()

    # Renderizar la plantilla con el formulario
    return render(request, 'registration/login.html', {'form': form})


# Create your views here.
def registro_cliente(request):
    # Si la solicitud es un POST, procesamos el formulario
    if request.method == 'POST':
        #se carga el formulario con los datos enviados
        form = RegistroClienteForm(request.POST)
        # Validamos el formulario
        if form.is_valid():
            # Guardamos el nuevo usuario
            form.save()
            # Mostramos un mensaje de éxito
            messages.success(request, "Cliente registrado correctamente. ¡Ya podés iniciar sesión!")
            # Redirigimos al usuario a la página de login
            return redirect(reverse('login'))
    else:
        # Si la solicitud es un GET, se muestra el formulario en blanco
        form = RegistroClienteForm()
    # Renderizamos la plantilla con el formulario
    return render(request, 'registration/register.html', {'form': form})