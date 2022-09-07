from django import forms
from projects.models import UserStoryType
from projects.usecase import ProjectUseCase
from projects.utils import build_field_error
from sga import widgets
from users.models import CustomUser
from projects.usecase import RoleUseCase
from projects.models import Permission

class FormCreateProject(forms.Form):

    name = forms.CharField(max_length=100, label='Nombre',
                           widget=widgets.TextInput())
    description = forms.CharField(
        max_length=100, label='Descripción', widget=widgets.TextInput())
    prefix = forms.CharField(
        max_length=5, label='Prefijo', widget=widgets.TextInput())
    scrum_master = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role_system='user'), label='Scrum Master', empty_label='Seleccione un usuario',
        widget=widgets.SelectInput())


class FormCreateProjectMember(forms.Form):
    """
    Formulario para crear un miembro de un proyecto
    """
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

class FormCreateRole(forms.Form):

    name_role = forms.CharField(max_length=100)  # nombre del rol
    description_role = forms.CharField(max_length=100)  # descripcion del rol
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(), widget=forms.CheckboxSelectMultiple())


class FormUserStoryType(forms.Form):
    """
    Formulario base para el modelo UserStoryType
    """
    name = forms.CharField(max_length=100, label='Nombre',
                           widget=widgets.TextInput())
    columns = forms.CharField(label='Columnas',
                              widget=widgets.TextInput(attrs={'placeholder': 'Ej: To Do, In Progress, Done'}))

    def custom_clean_columns(self, columns):
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
        return array_column


class FormCreateUserStoryType(FormUserStoryType):
    """
    Formulario para crear un tipo de historia de usuario en un proyecto
    """
    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id

    def clean(self):
        cleaned_data = super().clean()
        columns = cleaned_data.get('columns')
        name = cleaned_data.get('name')

        already_exists = UserStoryType.objects.filter(
            name=name, project_id=self.project_id).exists()
        if already_exists:
            raise forms.ValidationError(build_field_error(
                'name', 'Ya existe un tipo de historia con ese nombre'))
        print(columns)
        cleaned_data['columns'] = self.custom_clean_columns(columns)
        return cleaned_data


class FormEditUserStoryType(FormUserStoryType):
    """
    Formulario para editar un tipo de historia de usuario en un proyecto
    """
    def __init__(self, id, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.project_id = project_id

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        already_exists = UserStoryType.objects.filter(
            name=name, project_id=self.project_id).exclude(id=self.id).exists()
        if already_exists:
            raise forms.ValidationError(build_field_error(
                'name', 'Ya existe un tipo de historia con ese nombre'))

        columns = cleaned_data.get('columns')
        cleaned_data['columns'] = self.custom_clean_columns(columns)
        return cleaned_data
