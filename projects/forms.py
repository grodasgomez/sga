from django import forms
from datetime import datetime

from projects.utils import get_html_date


class FormCreateProject(forms.Form):

    name = forms.CharField(max_length=100, label='Nombre')
    description = forms.CharField(max_length=100, label='Descripción')
    prefix = forms.CharField(max_length=5, label='Prefijo')
    start_date = forms.DateField(
        label='Fecha Inicio', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(
        label='Fecha Fin', widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                'La fecha de inicio del proyecto debe ser menor a la fecha de finalización')
        return cleaned_data