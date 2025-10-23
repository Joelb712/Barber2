from django import forms
from Otros.models import Caja, MetodoPago

class AperturaCajaForm(forms.Form):
    monto_inicial = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Monto inicial",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

class MetodoForm(forms.ModelForm):
    class Meta:
        model = MetodoPago
        fields = ['nombre']