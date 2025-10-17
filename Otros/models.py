from django.db import models
from django.conf import settings

# Create your models here.

# --- CLIENTES ---
class Cliente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='clientes/', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
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
    foto = models.ImageField(upload_to='empleados/', blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_especialidad_display()})"

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
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"

# --- TURNO ---
class Turno(models.Model):
    cliente = models.ForeignKey("Cliente", on_delete=models.CASCADE)
    empleado = models.ForeignKey("Empleado", on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    horario = models.ForeignKey("Horario", on_delete=models.CASCADE)
    estado = models.ForeignKey("EstadoTurno", on_delete=models.CASCADE, default=1)

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
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.turno} - {self.servicio.nombre}"

# --- ESTADO DE TURNOS ---
class EstadoTurno(models.Model):
    choices = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    nombre = models.CharField(max_length=50,choices=choices  , unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
# --- CAJA ---
class Caja(models.Model):
    empleado = models.ForeignKey("Empleado", on_delete=models.CASCADE)  # recepcionista/gerente
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.BooleanField(default=True)  # True = abierta, False = cerrada

    def __str__(self):
        return f"Caja {self.id} - {'Abierta' if self.estado else 'Cerrada'}"

# --- MOVIMIENTO DE CAJA ---
class MovimientoCaja(models.Model):
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    ]
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name="movimientos")
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    empleado = models.ForeignKey("Empleado", on_delete=models.SET_NULL, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo} - {self.monto} ({self.fecha})"
    
# --- VENTA ---
class Venta(models.Model):
    cliente = models.ForeignKey("Cliente",on_delete=models.CASCADE)  # o FK si tenés tabla Clientes
    empleado = models.ForeignKey("Empleado", on_delete=models.CASCADE)  # quien registró la venta
    caja = models.ForeignKey("Caja", on_delete=models.CASCADE)  # debe estar abierta
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        estado= "Activa" if self.activo else "Cancelada"
        return f"Venta {self.id} - {self.cliente} ({estado})"

# --- DETALLE DE VENTA ---
class DetalleVenta(models.Model):
    venta = models.ForeignKey("Venta", on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey("Producto", on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


# --- MOVIMIENTO DE STOCK ---
class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]

    producto = models.ForeignKey("Producto", on_delete=models.CASCADE, related_name="movimientos_stock")
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(max_length=100, blank=True, null=True)  # ejemplo: Venta, Reposición, Ajuste
    empleado = models.ForeignKey("Empleado", on_delete=models.SET_NULL, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo} {self.cantidad} {self.producto.nombre}"

# --- METODOS DE PAGO ---
class MetodoPago(models.Model):
    nombre= models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre}"
    
# --- PAGOS ---
class Pago(models.Model):
    venta= models.ForeignKey("Venta", on_delete=models.CASCADE, related_name="pagos")
    metodo_pago= models.ForeignKey("MetodoPago", on_delete=models.CASCADE)
    monto= models.DecimalField(max_digits=10 , decimal_places=2)
    fecha_pago= models.DateTimeField(auto_now_add=True)
    estado= models.BooleanField(default=True)

    def __str__(self):
        return f"{self.metodo_pago.nombre} - {self.monto} -{self.estado}"
