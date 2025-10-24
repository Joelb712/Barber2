from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from Otros.models import Cliente, Empleado

from django.contrib.auth.forms import AuthenticationForm

estilos_formulario = 'w-full pl-14 pr-4 py-3 form-input text-white rounded-md bg-neutral-700'

class LoginUsuarioForm(AuthenticationForm):
    # Personaliza el campo 'username'
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingresa tu usuario',
            'class': estilos_formulario
        })
    )
    # Personaliza el campo 'password'
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingresa tu contraseña',
            'class': estilos_formulario
        }))
    




class RegistroClienteForm(UserCreationForm):
    telefono_validator = RegexValidator(
        regex=r'^\+?\d{7,15}$',
        message='El número debe contener solo dígitos y puede comenzar con +. Ej: +543871234567'
    )

    telefono = forms.CharField(
        required=False,
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={
            'id':'telefono',
            'class': estilos_formulario,
            'placeholder': 'Teléfono (Opcional)'
        }),
        help_text='Ej: +54 387 1234567'
    )
    dni = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': estilos_formulario, 'placeholder': 'DNI (Opcional)'}),
                          help_text='ej: 12345678')
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': estilos_formulario, 'placeholder': 'Correo electrónico'}),help_text='Ingresa una dirección de correo electrónico válida.')
    first_name = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': estilos_formulario, 'placeholder': 'Nombre'}),label='Nombre')
    last_name = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': estilos_formulario, 'placeholder': 'Apellido'}),label='Apellido')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'dni', 'password1', 'password2')

        
    def __init__(self, *args, **kwargs):
        super(RegistroClienteForm, self).__init__(*args, **kwargs)
        # Le damos un estilo a los campos que UserCreationForm maneja por defecto
        self.fields['username'].widget.attrs.update({'class': estilos_formulario, 'placeholder': 'Nombre de usuario'})
        self.fields['password1'].widget.attrs.update({'class': estilos_formulario, 'placeholder': 'Contraseña'})
        self.fields['password1'].help_text = 'La contraseña debe tener al menos 8 caracteres y como maximo 22 caracteres.' \
        ' Debe contener al menos una letra y un número.' \

        self.fields['password2'].widget.attrs.update({'class': estilos_formulario, 'placeholder': 'Confirmar contraseña'})
        self.fields['password2'].help_text = 'Ingrese la misma contraseña para verificación.'
        
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            import re
            if not re.fullmatch(r'^\+?\d{7,15}$', telefono):
                raise forms.ValidationError("El teléfono debe contener solo números y puede comenzar con +.")
        return telefono

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def save(self, commit=True):

        user = super().save(commit=False)
        user.email= self.cleaned_data.get('email')
        # Crear cliente vinculado al user
        if commit:
            user.save()
            Cliente.objects.create(
                user=user,
                first_name=self.cleaned_data.get('first_name') ,
                last_name=self.cleaned_data.get('last_name') ,
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
    
# class PerfilEmpleadoEditarForm(forms.ModelForm):
#     email = forms.EmailField(required=True, label="Correo electrónico")

#     class Meta:
#         model = Empleado
#         fields = ['telefono', 'dni', 'foto']

#     def __init__(self, *args, **kwargs):
#         self.user_instance = kwargs.pop('user_instance', None)
#         super().__init__(*args, **kwargs)
#         if self.user_instance:
#             self.fields['email'].initial = self.user_instance.email

#     def save(self, commit=True):
#         empleado = super().save(commit=False)
#         if self.user_instance:
#             self.user_instance.email = self.cleaned_data['email']
#             if commit:
#                 self.user_instance.save()
#                 empleado.save()
#         return empleado