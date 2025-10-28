from django import forms
from Otros.models import Servicio

Style_Servicio ='w-full py-2 pl-10 pr-4 rounded-lg border border-yellow-400 bg-gray-700 text-white placeholder-gray-400'

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'duracion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': Style_Servicio, 'placeholder': 'Nombre del servicio'}),
            'descripcion': forms.Textarea(attrs={'class': Style_Servicio, 'rows': 3, 'placeholder': 'Descripción opcional'}),
            'precio': forms.NumberInput(attrs={'class': Style_Servicio, 'step': '0.01'}),
            'duracion': forms.NumberInput(attrs={'class': Style_Servicio, 'min': 1}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'duracion': 'Duración (minutos)',
        }
