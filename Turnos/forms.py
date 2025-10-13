from django import forms
from Otros.models import Horario,Turno

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['hora_inicio', 'hora_fin']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['cliente','empleado','fecha','horario']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d' ),
            'horario': forms.Select(attrs={'type': 'time', 'class': 'form-control'}),
        }
        labels = {
            'cliente': 'Cliente',
            'empleado': 'Barbero',
            'fecha': 'Fecha',
            'horario': 'Hora',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convertir fecha a formato yyyy-MM-dd si ya tiene valor
        if self.instance and self.instance.fecha:
            self.initial['fecha'] = self.instance.fecha.strftime('%Y-%m-%d')
