from django import forms
from main.models import Anime
class SimpleForm(forms.Form):
    number = forms.IntegerField()

class AnimeFormatoForm(forms.Form):
    formatos_choices = list({(formato, formato) for formato in Anime.objects.values_list('formato_emision', flat=True).distinct()})
    formato_emision = forms.ChoiceField(choices=[('', 'Selecciona un formato')] + formatos_choices, required=True)

class IDUsuarioForm(forms.Form):
    idusuario = forms.IntegerField()