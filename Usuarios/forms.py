from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from Otros.models import Cliente, Empleado

class RegistroClienteForm(UserCreationForm):
    first_name = forms.CharField(required=True, label="Nombre")
    last_name = forms.CharField(required=True, label="Apellido")
    email = forms.EmailField(required=True)
    telefono = forms.CharField(required=False, label="Teléfono")
    dni = forms.CharField(required=False, label="DNI")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'dni', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit)
        # Crear cliente vinculado al user
        Cliente.objects.create(
            user=user,
            telefono=self.cleaned_data.get('telefono'),
            dni=self.cleaned_data.get('dni')
        )
        # Asignar grupo Cliente automáticamente
        grupo_cliente, created = Group.objects.get_or_create(name='Cliente')
        user.groups.add(grupo_cliente)
        return user
    
class EmpleadoCreateForm(forms.ModelForm):
    username = forms.CharField(required=True, label="Nombre de usuario")
    first_name = forms.CharField(required=True, label="Nombre")
    last_name = forms.CharField(required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Correo electrónico")
    password = forms.CharField(required=False, label="Contraseña (opcional)", widget=forms.PasswordInput)

    class Meta:
        model = Empleado
        fields = ['dni', 'telefono', 'especialidad']

    def save(self, commit=True):
        # Crear usuario
        password = self.cleaned_data.get('password') or "cambiame123"  # genérica si no se pasa
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=password
        )

        # Crear perfil de empleado
        empleado = Empleado.objects.create(
            user=user,
            dni=self.cleaned_data['dni'],
            telefono=self.cleaned_data['telefono'],
            especialidad=self.cleaned_data['especialidad']
        )

        # Asignar grupo automáticamente
        especialidad = self.cleaned_data['especialidad']
        if especialidad == 'barbero':
            grupo_name = 'Barbero'
        elif especialidad == 'recepcionista':
            grupo_name = 'Recepcionista'
        else:
            grupo_name = 'Gerente'

        grupo, created = Group.objects.get_or_create(name=grupo_name)
        user.groups.add(grupo)

        return empleado
    
class EmpleadoEditarForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Correo electrónico")  # solo email editable

    class Meta:
        model = Empleado
        fields = ['telefono', 'dni', 'especialidad', 'activo']  # campos del empleado que se pueden cambiar

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        if self.user_instance:
            self.fields['email'].initial = self.user_instance.email

    def save(self, commit=True):
        empleado = super().save(commit=False)
        if self.user_instance:
            self.user_instance.email = self.cleaned_data['email']
            if commit:
                self.user_instance.save()
                empleado.save()
        return empleado