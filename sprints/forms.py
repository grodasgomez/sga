from django import forms
from projects.models import Project

from sprints.models import Sprint, SprintMember
from sga import widgets
from sprints.usecase import SprintUseCase
from users.models import CustomUser
from user_stories.models import UserStoryComment
from projects.utils import build_field_error

class SprintCreateForm(forms.Form):
    """
    Formulario para crear un nuevo sprint
    """
    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id

    duration = forms.IntegerField(
        label='Duración en días',
        widget=widgets.NumberInput(attrs={'class': 'form-control'}),
        min_value=1,
        max_value=30,
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        if(SprintUseCase.exists_created_sprint(self.project_id)):
            raise forms.ValidationError('Ya existe un sprint en planeación')
        return cleaned_data


class SprintMemberCreateForm(forms.Form):
    """
    Formulario para crear un nuevo miembro de sprint
    """
    def __init__(self, project_id, sprint_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['workload'] = forms.IntegerField(label='Carga de trabajo', min_value=1,
                                                     max_value=12, widget=widgets.TextInput(attrs={'type': 'number'}))
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

class FormCreateComment(forms.Form):
    """
    Formulario para crear un comentario
    """
    def __init__(self, user_story_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_story_id = user_story_id
        self.fields['comment'] = forms.CharField(max_length=100, label='Comentario',widget=widgets.TextInput())  # Comentario

    def clean(self):
        cleaned_data = super().clean()
        comment = cleaned_data.get('comment')
        already_exists = UserStoryComment.objects.filter(
            comment=comment, user_story_id=self.user_story_id).exists()
        if already_exists:
            raise forms.ValidationError(build_field_error(
                'title', 'Ya existe este comentario'))
        return cleaned_data