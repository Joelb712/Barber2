from django import forms
from Otros.models import Cliente
estilos_formulario = 'w-full py-2 pl-10 pr-4 rounded-lg border border-yellow-400 bg-gray-700 text-white placeholder-gray-400'
# estilos_formulario = 'w-full pl-10 pr-10 py-3 border border-yellow-500 bg-neutral-700 text-white rounded-md'

class ClienteAltaForm(forms.ModelForm):
    first_name  = forms.CharField(
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={ 
            'class': estilos_formulario}))
    
    last_name = forms.CharField(
        required=True,
        label="Apellido", 
        widget=forms.TextInput(attrs={
            'class': estilos_formulario}))

    telefono = forms.CharField(
        required=True,
        label="Telefono",
        widget=forms.TextInput(attrs={
            'id':'telefono',
            'class': estilos_formulario}))
    
    dni = forms.CharField(
        required=True,
        label="DNI",
        widget=forms.TextInput(attrs={
            'class': estilos_formulario}))

    
    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'telefono', 'dni']

class ClienteEditarForm(forms.ModelForm):
    first_name  = forms.CharField(
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={ 
        'class': estilos_formulario}))

    last_name = forms.CharField(
        required=True,
        label="Apellido", 
        widget=forms.TextInput(attrs={
        'class': estilos_formulario}))

    telefono = forms.CharField(
        required=True,
        label="Telefono",
        widget=forms.TextInput(attrs={
        'id':'telefono',
        'class': estilos_formulario}))

    dni = forms.CharField(
        required=True,
        label="DNI",
        widget=forms.TextInput(attrs={
        'class': estilos_formulario}))


    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'telefono', 'dni', 'activo']