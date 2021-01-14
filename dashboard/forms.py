#form learned from https://www.youtube.com/watch?v=3XOS_UpJirU

from django import forms

class PersonForm(forms.Form):
    person = forms.CharField(label='')