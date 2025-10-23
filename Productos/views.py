from django.shortcuts import render, get_object_or_404
from .models import Producto
from .forms import ProductoForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from django.http import JsonResponse


def es_gerente(user):
    return user.groups.filter(name="Gerente").exists() or user.groups.filter(name="Recepcionista").exists() or user.is_superuser

@login_required
@user_passes_test(es_gerente)
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})

@login_required
@user_passes_test(es_gerente)
def tabla_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos_tabla.html', {'productos': productos})


@login_required
@user_passes_test(es_gerente)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Enviamos éxito para que el modal se cierre y la tabla se recargue
            return JsonResponse({'success': True})
        else:
            return render(request, 'formprod.html', {'form': form})
    else:
        form = ProductoForm()
        return render(request, 'formprod.html', {'form': form})

@login_required
@user_passes_test(es_gerente)
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES , instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return JsonResponse({'success': True})
        else:
            return render(request, 'formprod.html', {'form': form, 'producto': producto})
    else:
        form = ProductoForm(instance=producto)
        return render(request, 'formprod.html', {'form': form, 'producto': producto})

@login_required
@user_passes_test(es_gerente)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.activo= False
        producto.save()
        messages.success(request, 'Se dió de baja el producto correctamente.')
        return JsonResponse({'success': True})
    return render(request, 'eliminarprod.html', {'producto': producto})

#=======================
#PARA VER LOS PRODUCTOS EN EL INDEX
#========================
def get_productos(request):
    productos = Producto.objects.filter(activo=True).values('id', 'nombre', 'precio', 'imagen')
    return JsonResponse(list(productos), safe=False)
