from django import forms

class Upload(forms.Form):
    image = forms.ImageField()
