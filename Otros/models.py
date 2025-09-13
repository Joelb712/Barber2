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

# --- PRODUCTOS ---
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.precio}"

# --- SERVICIOS ---
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
# --- HORARIO (fijos de 30 min) ---
class Horario(models.Model):
    hora_inicio = models.TimeField(unique=True)
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"

# --- TURNO ---
class Turno(models.Model):
    cliente = models.ForeignKey("Cliente", on_delete=models.CASCADE)
    empleado = models.ForeignKey("Empleado", on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    horario = models.ForeignKey("Horario", on_delete=models.CASCADE)
    estado = models.ForeignKey("EstadoTurno", on_delete=models.CASCADE)

    duracion_real = models.PositiveIntegerField(default=30, help_text="En minutos")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('empleado', 'fecha', 'horario')

    def __str__(self):
        return f"{self.fecha} {self.horario} - {self.cliente}"

# --- SERVICIOS POR TURNO ---
class ServiciosXTurno(models.Model):
    turno = models.ForeignKey("Turno", on_delete=models.CASCADE, related_name="servicios_turno")
    servicio = models.ForeignKey("Servicio", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.turno} - {self.servicio.nombre}"

# --- ESTADO DE TURNOS ---
class EstadoTurno(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre