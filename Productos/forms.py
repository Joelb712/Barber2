from django import forms
from Otros.models import Producto

EstilosProducto='w-full py-2 pl-10 pr-4 rounded-lg border border-yellow-400 bg-gray-700 text-white placeholder-gray-400'


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'stock_actual', 'descripcion','imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': EstilosProducto, 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': EstilosProducto, 'rows': 3, 'placeholder': 'Descripción'}),
            'precio': forms.NumberInput(attrs={'class': EstilosProducto, 'step': '0.01', 'placeholder': 'Precio'}),
            'stock_actual': forms.NumberInput(attrs={'class': EstilosProducto, 'min': 0, 'placeholder': 'Stock disponible'}),
            'imagen': forms.ClearableFileInput(attrs={}),}
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'stock_actual': 'Stock',
            'activo': 'Disponible',
            'imagen': 'Imagen',
        }