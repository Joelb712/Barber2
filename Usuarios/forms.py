from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from Otros.models import Cliente, Empleado

# ==========================================================
# VALIDADORES PERSONALIZADOS
# ==========================================================

validator_nombre = RegexValidator(
    regex=r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$',
    message='Solo se permiten letras, acentos y espacios.'
)

validator_username = RegexValidator(
    regex=r'^[A-Za-z0-9]+$',
    message='El nombre de usuario solo puede contener letras y números (sin espacios).'
)

validator_dni = RegexValidator(
    regex=r'^\d{7,10}$',
    message='El DNI debe contener solo números (7 a 10 dígitos).'
)

validator_telefono = RegexValidator(
    regex=r'^\d{6,15}$',
    message='El teléfono debe contener solo números (6 a 15 dígitos).'
)

# ==========================================================
# ESTILOS
# ==========================================================

estilos_formulario = 'w-full pl-14 pr-4 py-3 form-input text-white rounded-md bg-neutral-700'
estilos_Empleado = 'w-full py-2 pl-10 pr-4 rounded-lg border border-yellow-400 bg-gray-700 text-white placeholder-gray-400'

# ==========================================================
# LOGIN
# ==========================================================

class LoginUsuarioForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingresa tu usuario',
            'class': estilos_formulario
        })
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingresa tu contraseña',
            'class': estilos_formulario
        })
    )

# ==========================================================
# REGISTRO DE CLIENTE
# ==========================================================

class RegistroClienteForm(UserCreationForm):

    telefono = forms.CharField(
        required=False,
        validators=[validator_telefono],
        widget=forms.TextInput(attrs={
            'id': 'telefono',
            'class': estilos_formulario,
            'placeholder': 'Teléfono'
        }),
        help_text='Solo números, mínimo 6 dígitos.'
    )

    dni = forms.CharField(
        required=False,
        validators=[validator_dni],
        widget=forms.TextInput(attrs={
            'id': 'dni',
            'class': estilos_formulario,
            'placeholder': 'DNI'
        }),
        help_text='Ingrese solo números.'
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': estilos_formulario,
            'placeholder': 'Correo electrónico'
        }),
        help_text='Debe ser un correo válido.'
    )

    first_name = forms.CharField(
        required=False,
        label='Nombre',
        validators=[validator_nombre],
        widget=forms.TextInput(attrs={
            'class': estilos_formulario,
            'placeholder': 'Nombre'
        })
    )

    last_name = forms.CharField(
        required=False,
        label='Apellido',
        validators=[validator_nombre],
        widget=forms.TextInput(attrs={
            'class': estilos_formulario,
            'placeholder': 'Apellido'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'telefono', 'dni', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Username sin espacios
        self.fields['username'].validators = [validator_username]
        self.fields['username'].widget.attrs.update({
            'class': estilos_formulario,
            'placeholder': 'Nombre de usuario'
        })

        # Passwords personalizados
        self.fields['password1'].widget.attrs.update({
            'class': estilos_formulario,
            'placeholder': 'Contraseña'
        })
        self.fields['password1'].help_text = (
            'La contraseña debe tener al menos 8 caracteres, incluir letras y números.'
        )

        self.fields['password2'].widget.attrs.update({
            'class': estilos_formulario,
            'placeholder': 'Confirmar contraseña'
        })
        self.fields['password2'].help_text = 'Repite la contraseña.'

    # ========== VALIDACIONES SERVER-SIDE ==========

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if " " in username:
            raise forms.ValidationError("El nombre de usuario no puede tener espacios.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')

        if commit:
            user.save()

            Cliente.objects.create(
                user=user,
                first_name=self.cleaned_data.get('first_name'),
                last_name=self.cleaned_data.get('last_name'),
                telefono=self.cleaned_data.get('telefono'),
                dni=self.cleaned_data.get('dni')
            )

            grupo_cliente, _ = Group.objects.get_or_create(name='Cliente')
            user.groups.add(grupo_cliente)

        return user

# ==========================================================
# CREAR EMPLEADO
# ==========================================================

class EmpleadoCreateForm(forms.ModelForm):

    username = forms.CharField(
        required=True,
        label="Nombre de usuario",
        validators=[validator_username],
        widget=forms.TextInput(attrs={'class': estilos_Empleado})
    )

    first_name = forms.CharField(
        required=True,
        label="Nombre",
        validators=[validator_nombre],
        widget=forms.TextInput(attrs={'class': estilos_Empleado})
    )

    last_name = forms.CharField(
        required=True,
        label="Apellido",
        validators=[validator_nombre],
        widget=forms.TextInput(attrs={'class': estilos_Empleado})
    )

    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': estilos_Empleado})
    )

    password = forms.CharField(
        required=False,
        label="Contraseña (opcional)",
        widget=forms.PasswordInput(attrs={'class': estilos_Empleado})
    )

    dni = forms.CharField(
        required=True,
        label='DNI',
        validators=[validator_dni],
        widget=forms.TextInput(attrs={'class': estilos_Empleado})
    )

    telefono = forms.CharField(
        required=True,
        label='Teléfono',
        validators=[validator_telefono],
        widget=forms.TextInput(attrs={'class': estilos_Empleado})
    )

    class Meta:
        model = Empleado
        fields = [
            'username', 'password', 'first_name', 'last_name',
            'especialidad', 'email', 'dni', 'telefono'
        ]
        widgets = {
            'especialidad': forms.Select(attrs={'class': estilos_Empleado}),
        }

    def save(self, commit=True):
        password = self.cleaned_data.get('password') or "cambiame123"

        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=password
        )

        empleado = Empleado.objects.create(
            user=user,
            dni=self.cleaned_data['dni'],
            telefono=self.cleaned_data['telefono'],
            especialidad=self.cleaned_data['especialidad']
        )

        grupo_name = (
            'Barbero' if self.cleaned_data['especialidad'] == 'barbero'
            else 'Recepcionista' if self.cleaned_data['especialidad'] == 'recepcionista'
            else 'Gerente'
        )

        grupo, _ = Group.objects.get_or_create(name=grupo_name)
        user.groups.add(grupo)

        return empleado

# ==========================================================
# EDITAR EMPLEADO
# ==========================================================

class EmpleadoEditarForm(forms.ModelForm):

    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': estilos_Empleado})
    )

    telefono = forms.CharField(
        required=True,
        label='Teléfono',
        validators=[validator_telefono],
        widget=forms.TextInput(attrs={'class': estilos_Empleado})
    )

    dni = forms.CharField(
        required=True,
        label='DNI',
        validators=[validator_dni],
        widget=forms.TextInput(attrs={'class': estilos_Empleado})
    )

    class Meta:
        model = Empleado
        fields = ['telefono', 'dni', 'especialidad', 'email', 'activo']
        widgets = {
            'especialidad': forms.Select(attrs={'class': estilos_Empleado}),
        }

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
