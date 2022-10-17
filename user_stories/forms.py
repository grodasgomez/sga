from django import forms
from projects.models import Project, UserStoryType, Role
from projects.usecase import ProjectUseCase
from projects.utils import build_field_error
from sga import widgets
from users.models import CustomUser
from sprints.models import Sprint, SprintMember
from projects.usecase import RoleUseCase
from projects.models import Permission
from user_stories.models import UserStory
from sprints.usecase import SprintUseCase

class FormRestoreUserStoryHistory(forms.Form):
    """
    Formulario para restaurar una historia de usuario a una version
    """
    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.fields['code'] = forms.CharField(max_length=100, label='Codigo',widget=widgets.TextInput())  # Codigo del US
        self.fields['title'] = forms.CharField(max_length=100, label='Titulo',widget=widgets.TextInput())  # TITULO del US
        self.fields['description'] = forms.CharField(max_length=100, label='Descripcion',widget=widgets.TextInput())  # descripcion del US
        self.fields['business_value'] = forms.IntegerField( min_value=1, max_value=100 ,label='Valor de Negocio',widget=widgets.NumberInput())  # Valor de Negocio del US
        self.fields['technical_priority'] = forms.IntegerField(min_value=1, max_value=100 ,label='Prioridad Tecnica',widget=widgets.NumberInput())  # Prioridad Tecnica del US
        self.fields['estimation_time'] = forms.IntegerField(min_value=1, max_value=100 , label='Tiempo estimado',widget=widgets.NumberInput())  # Tiempo estimado del US
        self.fields['sprint_priority'] = forms.IntegerField(min_value=1, max_value=100 , label='Prioridad para Sprint',widget=widgets.NumberInput())  # Prioridad para Sprint
        self.fields['us_type'] = forms.ModelChoiceField(
            queryset=ProjectUseCase.filter_user_story_type_by_project(project_id), label='Tipo de Historia de Usuario',
            empty_label='Seleccione un tipo',
            widget=widgets.SelectInput()
        )
        self.fields['column'] = forms.IntegerField(min_value=1, max_value=100 , label='Columna',widget=widgets.NumberInput())  # Columna
        self.fields['sprint'] = forms.ModelChoiceField(
            queryset=Sprint.objects.all(), label='Sprint',
            empty_label='Sprint no Asignado',
            widget=widgets.SelectInput()
        )
        self.fields['sprint_member'] = forms.ModelChoiceField(
            queryset=SprintMember.objects.all(), label='Miembro asignado',
            empty_label='Miembro no asignado',
            widget=widgets.SelectInput()
        )