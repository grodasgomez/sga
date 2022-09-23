from django import forms
from projects.models import Project

from sprints.models import Sprint, SprintMember
from sga import widgets
from sprints.usecase import SprintUseCase
from users.models import CustomUser


class SprintMemberCreateForm(forms.Form):
    """
    Formulario para crear un nuevo miembro de sprint
    """

    def __init__(self, project_id, sprint_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['workload'] = forms.IntegerField(label='Carga de trabajo', min_value=1,
                                                     max_value=8, widget=widgets.TextInput(attrs={'type': 'number'}))
        self.fields['user'] = forms.ModelChoiceField(
            queryset=SprintUseCase.get_addable_users(project_id, sprint_id),
            empty_label='Seleccione un usuario',
            label='Usuario', widget=widgets.SelectInput())




class SprintStartForm(forms.ModelForm):
    """
    Formulario para iniciar un sprint

    """
    class Meta:
        model = Sprint
        fields = ['capacity', 'duration', 'start_date']
        widgets = {
            'capacity': widgets.TextInput(attrs={'type': 'number'}),
            'duration': widgets.TextInput(attrs={'type': 'number'}),
            'start_date': widgets.DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['capacity'].label = 'Capacidad en horas'
        self.fields['duration'].label = 'Duración en días'
        self.fields['start_date'].label = 'Fecha de inicio'
