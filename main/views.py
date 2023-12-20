from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
import shelve 
from main.models import Anime, Puntuacion
from main import populateDB
from main.forms import AnimeFormatoForm, IDUsuarioForm
from main.recommendations import transformPrefs, calculateSimilarItems, getRecommendations, getRecommendedItems, topMatches, sim_distance
# Create your views here.

def loadDict():
    Prefs={}   # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("dataRS.dat")
    ratings = Puntuacion.objects.all()
    for ra in ratings:
        user = ra.idUsuario
        itemid = ra.animeid.animeID
        rating = ra.puntuacion
        Prefs.setdefault(user, {})
        Prefs[user][itemid] = rating
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf['SimItems']=calculateSimilarItems(Prefs, n=10)
    shelf.close()

#Funcion de acceso restringido que carga los datos en la BD
@login_required(login_url='/ingresar')
def cargar(request):
    (o,g)= populateDB.populate()
    informacion="Datos cargados correctamente\n" + "Animes: " + str(o) + " ; " + "Puntuaciones: " + str(g)
    logout(request)
    return render(request, 'cargar.html', {'titulo':'FIN DE CARGA DE LA BD','inf':informacion})

def loadRS(request):
    loadDict()
    mensaje = 'Se han cargado la matriz y la matriz invertida '
    return render(request, 'mensaje.html',{'titulo':'FIN DE CARGA DEL RS','mensaje':mensaje})

def home(request):
    return render(request, 'home.html')

def ingresar(request):
    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return (HttpResponseRedirect('/cargar'))
            else:
                return render(request, 'mensaje_error.html',{'error':"USUARIO NO ACTIVO"})
        else:
            return render(request, 'mensaje_error.html',{'error':"USUARIO O CONTRASEYA INCORRECTOS"})
                     
    return render(request, 'ingresar.html', {'formulario':formulario})

def anime_list(request):
    if request.method == 'POST':
        form = AnimeFormatoForm(request.POST)
        if form.is_valid():
            formato_seleccionado = form.cleaned_data['formato_emision']
            animes = Anime.objects.filter(formato_emision=formato_seleccionado, num_episodios__gt=5).order_by('num_episodios').reverse()
            return render(request, 'anime_list_formato.html', {'form': form, 'animes': animes})
    else:
        form = AnimeFormatoForm()

    return render(request, 'anime_list_formato.html', {'form': form})

def animes_mas_vistos(request):
    diccionario_anime_items={}
    diccionario={}
    lista_ordenada=[]
    lista_de_los_animes_mas_puntuados=[]
    todos_los_animes=Anime.objects.all()
    for objeto in todos_los_animes:
        lista_ordenada.append(len(objeto.puntuacion_set.all()))
        diccionario[objeto]=len(objeto.puntuacion_set.all())
    for val in diccionario:
        if lista_ordenada[:3].__contains__(diccionario[val]):
            lista_de_los_animes_mas_puntuados.append(val)
    # # lista3 = lista_de_los_animes_mas_puntuados[:3]
    # # for anime in lista3:
    # #     idAnime = anime.animeID
    # #     shelf = shelve.open("dataRS.dat") 
    # #     Prefs = shelf['ItemsPrefs']
    # #     shelf.close()
    # #     #utilizo distancia euclidea para que se vea mejor en los listados
    # #     parecidas = topMatches(Prefs, int(idAnime),n=2,similarity=sim_distance)
    # #     animes = []
    # #     similaridad = []
    # #     for re in parecidas:
    # #         animes.append(Anime.objects.get(pk=re[1]))
    # #         similaridad.append(re[0])
    # #         print(re[0])
    # #     items= zip(animes,similaridad)
    # #     diccionario_anime_items[anime.animeID]=items
    return render(request, 'animes_mas_vistos.html', {'animes': lista_de_los_animes_mas_puntuados[:3]})

def recomendar_anime_RSitems(request):
    formulario = IDUsuarioForm()
    items = None
    usuario = None

    if request.method=='POST':
        formulario = IDUsuarioForm(request.POST)

        if formulario.is_valid():
            idusuario=formulario.cleaned_data['idusuario']
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            SimItem = shelf['SimItems']
            shelf.close()
            rankings = getRecommendedItems(Prefs,SimItem,int(idusuario))
            recomendadas= rankings[:3]
            animes = []
            puntuaciones = []
            for re in recomendadas:
                animes.append(Anime.objects.get(pk=re[1]))
                puntuaciones.append(re[0])
            items= zip(animes,puntuaciones)

    return render(request, 'recomendar_anime_usuarios.html', {'formulario':formulario, 'items':items, idusuario:'idusuario'})

def recomendar_peliculas_usuario_RSusuario(request):
    formulario = IDUsuarioForm()
    items = None
    usuario = None

    if request.method=='POST':
        formulario = IDUsuarioForm(request.POST)

        if formulario.is_valid():
            idUsuario=formulario.cleaned_data['idusuario']
            
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            shelf.close()
            rankings = getRecommendations(Prefs,int(idUsuario))
            recomendadas= rankings[:2]
            animes = []
            puntuaciones = []
            for re in recomendadas:
                animes.append(Anime.objects.get(pk=re[1]))
                puntuaciones.append(re[0])
            items= zip(animes,puntuaciones)

    return render(request, 'recomendar.html', {'formulario':formulario, 'items':items})
    


""""
def recomendar_peliculas_usuario_RSusuario(request):
    formulario = UsuarioBusquedaForm()
    items = None
    usuario = None

    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)

        if formulario.is_valid():
            idUsuario=formulario.cleaned_data['idUsuario']
            usuario = get_object_or_404(Usuario, pk=idUsuario)
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            shelf.close()
            rankings = getRecommendations(Prefs,int(idUsuario))
            recomendadas= rankings[:2]
            peliculas = []
            puntuaciones = []
            for re in recomendadas:
                peliculas.append(Pelicula.objects.get(pk=re[1]))
                puntuaciones.append(re[0])
            items= zip(peliculas,puntuaciones)

    return render(request, 'recomendar_peliculas_usuarios.html', {'formulario':formulario, 'items':items, 'usuario':usuario})
    
def recomendar_peliculas_usuario_RSitems(request):
    formulario = UsuarioBusquedaForm()
    items = None
    usuario = None

    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)

        if formulario.is_valid():
            idUsuario=formulario.cleaned_data['idUsuario']
            usuario = get_object_or_404(Usuario, pk=idUsuario)
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            SimItem = shelf['SimItems']
            shelf.close()
            rankings = getRecommendedItems(Prefs,SimItem,int(idUsuario))
            recomendadas= rankings[:3]
            peliculas = []
            puntuaciones = []
            for re in recomendadas:
                peliculas.append(Pelicula.objects.get(pk=re[1]))
                puntuaciones.append(re[0])
            items= zip(peliculas,puntuaciones)

    return render(request, 'recomendar_peliculas_usuarios.html', {'formulario':formulario, 'items':items, 'usuario':usuario})

def mostrar_peliculas_parecidas(request):
    formulario = PeliculaBusquedaForm()
    pelicula = None
    items = None
    
    if request.method=='POST':
        formulario = PeliculaBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idPelicula = formulario.cleaned_data['idPelicula']
            pelicula = get_object_or_404(Pelicula, pk=idPelicula)
            shelf = shelve.open("dataRS.dat")
            ItemsPrefs = shelf['ItemsPrefs']
            shelf.close()
            #utilizo distancia euclidea para que se vea mejor en los listados
            parecidas = topMatches(ItemsPrefs, int(idPelicula),n=3,similarity=sim_distance)
            peliculas = []
            similaridad = []
            for re in parecidas:
                peliculas.append(Pelicula.objects.get(pk=re[1]))
                similaridad.append(re[0])
                print(re[0])
            items= zip(peliculas,similaridad)
    
    return render(request, 'peliculas_similares.html', {'formulario':formulario, 'pelicula': pelicula, 'items': items})

def mostrar_usuarios_pare_pelicula(request):
    formulario = PeliculaBusquedaForm()
    pelicula = None
    items = None
    
    if request.method=='POST':
        formulario = PeliculaBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idPelicula = formulario.cleaned_data['idPelicula']
            pelicula = get_object_or_404(Pelicula, pk=idPelicula)
            shelf = shelve.open("dataRS.dat")
            ItemsPrefs = shelf['ItemsPrefs']
            shelf.close()
            #utilizo distancia euclidea para que se vea mejor en los listados
            rankings = getRecommendations(ItemsPrefs, int(idPelicula))
            recomendadas= rankings[:3]
            usuario = []
            puntuaciones = []
            for re in recomendadas:
                usuario.append(Usuario.objects.get(pk=re[1]))
                puntuaciones.append(re[0])
            items= zip(usuario,puntuaciones)
    
    return render(request, 'usuarios_para_pelicula.html', {'formulario':formulario, 'pelicula': pelicula, 'items': items})

def mostrar_puntuaciones_usuario(request):
    formulario = UsuarioBusquedaForm()
    puntuaciones = None
    idusuario = None
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idusuario = formulario.cleaned_data['idUsuario']
            puntuaciones = Puntuacion.objects.filter(idUsuario = Usuario.objects.get(pk=idusuario))
            
    return render(request, 'puntuaciones_usuario.html', {'formulario':formulario, 'puntuaciones':puntuaciones, 'idusuario':idusuario})
"""