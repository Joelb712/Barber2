from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def Inicio(request):
    return render(request, 'index.html')

@login_required
def dash(request):
    return render(request,'dash.html')

def contacto(request):
    return render(request,'contacto.html')
