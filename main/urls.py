from django.contrib import admin
from django.urls import path
from .views import home, cargar, ingresar, loadRS, anime_list, animes_mas_vistos, recomendar_anime_RSitems
urlpatterns = [
    path('', home, name='home'),
    path('cargar', cargar, name='cargar'),
    path('ingresar',ingresar, name='ingresar'),
    path('load-rs',loadRS, name='loadRS'),
    path('anime_list',anime_list, name='anime_list'),#apartado c
    path('animes_mas_vistos',animes_mas_vistos, name='animes_mas_vistos'),#apartado d
    path('recomendar',recomendar_anime_RSitems, name='recomendar')#apartado e
]