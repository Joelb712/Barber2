from django.db import models
from django.conf import settings

# Create your models here.

# --- CLIENTES ---
class Cliente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cliente: {self.user.username} - {self.user.first_name} {self.user.last_name}"
        return f"{self.first_name} {self.last_name}"

# --- EMPLEADOS ---
class Empleado(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    especialidad = models.CharField(
        max_length=50,
        choices=[('barbero', 'Barbero'), ('recepcionista', 'Recepcionista'), ('gerente', 'Gerente')]
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Empleado: {self.user.username} ({self.get_especialidad_display()})"
