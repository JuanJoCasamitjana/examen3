
#encoding:utf-8
from main.models import Puntuacion, Anime
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
import re
import csv

# lineas para evitar error SSL
path = "./data"

def populate():
    a=populateAnimes()
    p=populateRatings()  #USAMOS LOS DICCIONARIOS DE USUARIOS Y PELICULAS PARA ACELERAR LA CARGA EN PUNTUACIONES
    return (a,p)

def populateRatings():
    Puntuacion.objects.all().delete()
    ruta = path+"/ratings.csv"
    lista=[]
    with open(ruta, 'r', newline='') as archivo:
        lector_csv = csv.reader(archivo, delimiter=';')
        next(lector_csv)
        for l in lector_csv:
            anime = Anime.objects.get(pk=int(l[1]))
            lista.append(Puntuacion(idUsuario=int(l[0]),animeid=anime,puntuacion=int(l[2])))
    Puntuacion.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return Puntuacion.objects.count()

def populateAnimes():
    Anime.objects.all().delete()
    ruta = path+"/anime.csv"
    lista=[]
    with open(ruta, 'r', newline='') as archivo:
        lector_csv = csv.reader(archivo, delimiter=";")
        next(lector_csv)
        for fila in lector_csv:
            num_episodios = 0
            if fila[-1] != 'Unknown':
                num_episodios= int(fila[-1])
            lista.append(Anime(animeID=int(fila[0]),titulo=str(fila[1]), generos=str(fila[2]),formato_emision=str(fila[-2]), num_episodios=num_episodios))
    Anime.objects.bulk_create(lista)     

    
    return Anime.objects.count()

