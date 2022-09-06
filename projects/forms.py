from django import forms
from projects.usecase import ProjectUseCase
from projects.utils import build_field_error
from sga import widgets
from users.models import CustomUser
from users.usecase import RoleUseCase


class FormCreateProject(forms.Form):

    name = forms.CharField(max_length=100, label='Nombre',
                           widget=widgets.TextInput())
    description = forms.CharField(
        max_length=100, label='Descripción', widget=widgets.TextInput())
    prefix = forms.CharField(
        max_length=5, label='Prefijo', widget=widgets.TextInput())
    scrum_master = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(), label='Scrum Master', empty_label='Seleccione un usuario',
        widget=widgets.SelectInput())


class FormCreateProjectMember(forms.Form):

    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'] = forms.ModelChoiceField(
            queryset=ProjectUseCase.get_non_members(project_id), label='Miembro',
            empty_label='Seleccione un usuario',
            widget=widgets.SelectInput()
        )
        self.fields['roles'] = forms.ModelMultipleChoiceField(
            queryset=RoleUseCase.get_roles_by_project(project_id),
            label='Roles', widget=widgets.SelectMultipleInput())


class FormCreateUserStoryType(forms.Form):

    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id

    name = forms.CharField(max_length=100, label='Nombre',
                           widget=widgets.TextInput())
    columns = forms.CharField(label='Columnas',
                              widget=widgets.TextInput(attrs={'placeholder': 'Ej: To Do, In Progress, Done'}))

    def clean(self):
        cleaned_data = super().clean()
        columns = cleaned_data.get('columns')

        # Creo un array de los nombres de las columnas
        array_column = columns.split(',')

        array_column = [x.strip() for x in array_column]

        # Verifico que haya minimo dos columnas
        if len(array_column) < 2:
            raise forms.ValidationError(build_field_error(
                'columns', 'Debe ingresar al menos dos columnas'))

        # Verifico que no haya columnas repetidas
        if len(array_column) != len(set(array_column)):
            raise forms.ValidationError(build_field_error(
                'columns', 'No puede haber columnas repetidas'))

        # Verifico que no haya columnas vacias
        for column in array_column:
            if column == '':
                raise forms.ValidationError(build_field_error(
                    'columns', 'No puede haber columnas vacias'))

        cleaned_data['columns'] = array_column
        return cleaned_data
