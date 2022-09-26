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

class SprintMemberEditForm(forms.Form):
    """
    Formulario para cambiar la carga horaria de un miembro de un sprint
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    workload = forms.IntegerField(label='Carga de trabajo', min_value=1,
                                  max_value=12, widget=widgets.TextInput(attrs={'type': 'number'}))

class SprintStartForm(forms.ModelForm):
    """
    Formulario para iniciar un sprint
    """
    class Meta:
        model = Sprint
        fields = ['capacity', 'duration', 'start_date']
        widgets = {
            'duration': widgets.TextInput(attrs={'type': 'number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duration'].label = 'Duración en días'

class AssignSprintMemberForm(forms.Form):
    """
    Formulario para asignar un sprint member a una user story
    """
    def __init__(self, sprint_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sprint_member'] = forms.ModelChoiceField(
            queryset=SprintUseCase.get_assignable_sprint_members(sprint_id), label='Miembro',
            empty_label='Sin Asignar',
            widget=widgets.SelectInput(),
            required=False
        )
