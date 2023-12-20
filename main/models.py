from django.db import models

# Create your models here.

class Anime(models.Model):
    animeID = models.IntegerField(primary_key=True)
    titulo = models.TextField(null=True)
    generos = models.TextField(null=True)
    formato_emision = models.TextField(null=True)
    num_episodios = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.titulo} - Episodios: "
    
    class Meta:
        ordering = ('num_episodios', )

class Puntuacion(models.Model):
    idUsuario = models.PositiveIntegerField(null=True)
    animeid = models.ForeignKey(Anime, on_delete= models.CASCADE)
    puntuacion = models.PositiveSmallIntegerField()

    def __str__(self):
        return "Id del usuario: "+str(self.IdUsuario)