from django import forms
from Otros.models import Horario, Turno, Cliente, Empleado

# --- Estilos CSS ---
Style_ConIcono = 'w-full py-2 pl-10 pr-4 rounded-lg border border-yellow-400 bg-gray-700 text-white placeholder-gray-400'
Style_Normal = 'w-full py-2 px-4 rounded-lg border border-yellow-400 bg-gray-700 text-white placeholder-gray-400'


# ==========================================================
# FORMULARIO DE HORARIOS
# ==========================================================
class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['hora_inicio', 'hora_fin']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'class': Style_ConIcono, 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': Style_ConIcono, 'type': 'time'}),
        }


# ==========================================================
# FORMULARIO DE TURNOS
# ==========================================================

# Campo personalizado para Cliente (Muestra: DNI - Nombre Apellido)
class ClienteChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        dni_str = obj.dni if obj.dni else "S/DNI"
        return f"{dni_str} - {obj.first_name} {obj.last_name}"

# Campo personalizado para Empleado (Muestra: Nombre Apellido)
class BarberoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class TurnoForm(forms.ModelForm):
    # 1. Cliente: "Seleccionar Cliente"
    cliente = ClienteChoiceField(
        queryset=Cliente.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': Style_Normal}),
        label='Cliente',
        empty_label="Seleccionar Cliente"  # <--- Aquí cambiamos el texto
    )
    
    # 2. Empleado: "Seleccionar Profesional"
    empleado = BarberoChoiceField(
        queryset=Empleado.objects.filter(especialidad='barbero', activo=True),
        widget=forms.Select(attrs={'class': Style_ConIcono}),
        label='Empleado',
        empty_label="Seleccionar Profesional" # <--- Aquí cambiamos el texto
    )

    # 3. Horario: "Seleccionar Hora del Turno"
    # (Ahora lo definimos explícitamente para poder usar empty_label)
    horario = forms.ModelChoiceField(
        queryset=Horario.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': Style_ConIcono}),
        label='Horario',
        empty_label="Seleccionar Hora del Turno" # <--- Aquí cambiamos el texto
    )

    class Meta:
        model = Turno
        fields = ['cliente', 'empleado', 'fecha', 'horario']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date', 
                'class': Style_Normal,
                'style': 'color-scheme: dark;' 
            }, format='%Y-%m-%d'),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.fecha:
            self.initial['fecha'] = self.instance.fecha.strftime('%Y-%m-%d')