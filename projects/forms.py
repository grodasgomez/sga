from django import forms
from sga import widgets
from users.models import CustomUser


class FormCreateProject(forms.Form):

    name = forms.CharField(max_length=100, label='Nombre', widget=widgets.TextInput())
    description = forms.CharField(max_length=100, label='Descripción', widget=widgets.TextInput())
    prefix = forms.CharField(max_length=5, label='Prefijo', widget=widgets.TextInput())
    start_date = forms.DateField(
        label='Fecha Inicio', widget=widgets.DateInput())
    end_date = forms.DateField(
        label='Fecha Fin', widget=widgets.DateInput())
    scrum_master = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(), label='Scrum Master', empty_label='Seleccione un usuario',
        widget=widgets.SelectInput())

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                'La fecha de inicio del proyecto debe ser menor a la fecha de finalización')
        return cleaned_data