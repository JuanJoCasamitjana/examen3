from django import forms

class SimpleForm(forms.Form):
    number = forms.IntegerField()