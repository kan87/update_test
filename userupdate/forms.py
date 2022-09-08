# from django import forms
from django.forms import ModelForm
from userupdate.models import Pilot

# class NameForm(forms.Form):
#     e_id = forms.CharField(label='Employee ID', max_length=50)
#     first_name = forms.CharField(label='First Name', max_length=50)
#     last_name = forms.CharField(label='Last Name', max_length=50)
#     extra = forms.CharField(label='Extra', max_length=50)

class NameForm(ModelForm):
    class Meta:
        model = Pilot
        fields = ['e_id', 'first_name', 'last_name', 'extra', 'extra_locked']
