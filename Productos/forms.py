from django import forms
from Otros.models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio','imagen', 'stock_actual']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Precio'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Stock disponible'}),
            'imagen': forms.ClearableFileInput(attrs= {'class': 'form-control-file'}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'stock_actual': 'Stock',
            'activo': 'Disponible',
            'imagen': 'Imagen',
        }