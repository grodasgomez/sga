from django import forms


class FormCreateProject(forms.Form):

    name= forms.CharField(max_length=100, label='Nombre')
    description= forms.CharField(max_length=100, label='Descripción')
    prefix = forms.CharField(max_length=5, label='Prefijo')
    start_date= forms.DateField(label='Fecha Inicio',widget=forms.DateInput(attrs={'type': 'date'}))
    end_date= forms.DateField(label='Fecha Fin',widget=forms.DateInput(attrs={'type': 'date'}))

