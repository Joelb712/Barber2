from django import forms
from Otros.models import Caja, MetodoPago
Styles_='w-full py-2 pl-10 pr-4 rounded-lg border border-yellow-400 bg-gray-700 text-white placeholder-gray-400'

class AperturaCajaForm(forms.Form):
    monto_inicial = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Monto inicial",
        widget=forms.NumberInput(attrs={"class": Styles_})
    )

class MetodoForm(forms.ModelForm):
    class Meta:
        model = MetodoPago
        fields = ['nombre']
        labels={
            'nombre':'Nombre'
        }
        widgets = {
            'nombre': forms.Select(attrs={'class': Styles_})
        }