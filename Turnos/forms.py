from django import forms
from Otros.models import Horario,Turno, Empleado,Cliente
from datetime import date
from django.utils.dateparse import parse_date


Style_ ='w-full py-2 pl-10 pr-4 rounded-lg border border-yellow-400 bg-gray-700 text-white placeholder-gray-400'

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['hora_inicio', 'hora_fin']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'class': Style_, 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': Style_, 'type': 'time'}),
        }

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['cliente','empleado','fecha','horario']
        widgets = {
            'cliente': forms.Select(attrs={'class': Style_}),
            'empleado': forms.Select(attrs={'class': Style_}),
            'fecha': forms.DateInput(attrs={'type': 'date','class': Style_,'min': date.today().strftime('%Y-%m-%d')},format='%Y-%m-%d'),
            'horario': forms.Select(attrs={'class': Style_}),
        }
        labels = {
            'cliente': 'Cliente',
            'empleado': 'Barbero',
            'fecha': 'Fecha',
            'horario': 'Hora',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✔ Mostrar solo clientes activos
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)

        # ✔ Mostrar solo empleados barberos activos
        self.fields['empleado'].queryset = Empleado.objects.filter(
            especialidad='barbero',
            activo=True
        )

        # ✔ Formatear fecha correctamente si ya tiene valor
        if self.instance and self.instance.fecha:
            self.initial['fecha'] = self.instance.fecha.strftime('%Y-%m-%d')

        # ✔ Mostrar todos los horarios activos
        self.fields['horario'].queryset = Horario.objects.all()
    
    