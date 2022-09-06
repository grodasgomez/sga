from django import forms
from projects.usecase import ProjectUseCase
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

class FormRoles(forms.Form):

    name_role = forms.CharField(max_length=100)  # nombre del rol
    description_role = forms.CharField(max_length=100)  # descripcion del rol
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(), widget=forms.CheckboxSelectMultiple())

    # def clean(self):
    #     cleaned_data = super().clean()
    #     start_date = cleaned_data.get('start_date')
    #     end_date = cleaned_data.get('end_date')
    #     if start_date and end_date and start_date > end_date:
    #         raise forms.ValidationError(
    #             'La fecha de inicio del proyecto debe ser menor a la fecha de finalización')
    #     return cleaned_data
