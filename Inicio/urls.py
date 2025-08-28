from django.urls import path
from .views import *

urlpatterns=[
    path('',Inicio,name='Inicio'),
    path('dash',dash,name='dash'),
    path('contacto/',contacto,name='contacto'),
    path('tienda/',tienda,name='tienda'),
]
