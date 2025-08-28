from django import forms
from Otros.models import Cliente

class ClienteAltaForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'telefono', 'dni', 'notas', 'activo']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'telefono': 'Teléfono',
            'dni': 'DNI',
            'notas': 'Notas',
            'activo': 'Activo',
        }

class ClienteEditarForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'telefono', 'dni', 'notas', 'activo']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'telefono': 'Teléfono',
            'dni': 'DNI',
            'notas': 'Notas',
            'activo': 'Activo',
        }
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
        }