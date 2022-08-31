from django import forms

class NameForm(forms.Form):
    e_id = forms.CharField(label='Employee ID', max_length=50)
    first_name = forms.CharField(label='First Name', max_length=50)
    last_name = forms.CharField(label='Last Name', max_length=50)
    extra = forms.CharField(label='Extra', max_length=50)