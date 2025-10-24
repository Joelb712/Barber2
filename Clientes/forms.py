from django import forms
from Otros.models import Cliente
estilos_formulario = 'w-full px-4 py-2 rounded-lg border border-yellow-400 bg-gray-700 text-white placeholder-gray-400'
# estilos_formulario = 'w-full pl-10 pr-10 py-3 border border-yellow-500 bg-neutral-700 text-white rounded-md'

class ClienteAltaForm(forms.ModelForm):
    first_name  = forms.CharField(
    label="Nombre",
    widget=forms.TextInput(attrs={ 
        'placeholder': 'ingrese nombre',
        'class': estilos_formulario}))
    
    last_name = forms.CharField(
    label="Apellido", 
    widget=forms.TextInput(attrs={
        'placeholder': 'ingrese apellido',
        'class': estilos_formulario}))

    telefono = forms.CharField(
    label="Telefono",
    widget=forms.TextInput(attrs={
        'id':'telefono',
        'placeholder': 'ingrese telefono',
        'class': estilos_formulario}))
    
    dni = forms.CharField(
    label="DNI",
    widget=forms.TextInput(attrs={
        'placeholder': 'ingrese dni',
        'class': estilos_formulario}))

    notas = forms.CharField(
    label="Notas",
    widget=forms.Textarea(attrs={
        'rows': 3,
        'placeholder': 'ingrese nota',
        'class': estilos_formulario}))
    
    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'telefono', 'dni', 'notas']

class ClienteEditarForm(forms.ModelForm):
    first_name  = forms.CharField(
    label="Nombre",
    widget=forms.TextInput(attrs={ 
    'placeholder': 'ingrese nombre',
    'class': estilos_formulario}))

    last_name = forms.CharField(
    label="Apellido", 
    widget=forms.TextInput(attrs={
    'placeholder': 'ingrese apellido',
    'class': estilos_formulario}))

    telefono = forms.CharField(
    label="Telefono",
    widget=forms.TextInput(attrs={
    'id':'telefono',
    'placeholder': 'ingrese telefono',
    'class': estilos_formulario}))

    dni = forms.CharField(
    label="DNI",
    widget=forms.TextInput(attrs={
    'placeholder': 'ingrese dni',
    'class': estilos_formulario}))

    notas = forms.CharField(
    label="Notas",
    widget=forms.Textarea(attrs={
    'rows': 3,
    'placeholder': 'ingrese nota',
    'class': estilos_formulario}))

    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'telefono', 'dni', 'notas', 'activo']