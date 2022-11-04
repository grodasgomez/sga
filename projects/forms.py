from django import forms
from projects.models import Project, UserStoryType, Role, ProjectHoliday
from projects.usecase import ProjectUseCase
from projects.utils import build_field_error
from sga import widgets
from users.models import CustomUser
from projects.usecase import RoleUseCase
from projects.models import Permission
from user_stories.models import UserStory, UserStoryComment
from datetime import datetime

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

class FormDeleteProject(forms.Form):

    name = forms.CharField(max_length=100, label='Nombre',
                           widget=widgets.TextInput())
    description = forms.CharField(
        max_length=100, label='Descripción', widget=widgets.TextInput())
    prefix = forms.CharField(
        max_length=5, label='Prefijo', widget=widgets.TextInput())
    scrum_master = forms.CharField(
        max_length=100, label='Scrum Master', widget=widgets.TextInput())

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
            queryset=RoleUseCase.get_roles_by_project(project_id).exclude(name='Scrum Master'),
            label='Roles', widget=widgets.SelectMultipleInput())

class FormEditProjectMember(forms.Form):
    """
    Formulario para editar un miembro de un proyecto
    """
    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = forms.CharField(max_length=100, label='Miembro',widget=widgets.TextInput(attrs={'readonly': 'readonly'}))
        self.fields['roles'] = forms.ModelMultipleChoiceField(
            queryset=RoleUseCase.get_roles_by_project(project_id).exclude(name='Scrum Master'),
            label='Roles', widget=widgets.SelectMultipleInput())

class FormCreateRole(forms.Form):
    """
    Formulario para crear y editar roles de un proyecto
    """

    name = forms.CharField(max_length=100, label='Nombre',widget=widgets.TextInput())  # nombre del rol
    description = forms.CharField(max_length=100, label='Descripcion',widget=widgets.TextInput())  # descripcion del rol
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'with_select_all'}), label='Permisos')

    def __init__(self, project_id, id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.project_id = project_id

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if(self.id): #editar roles, ya tienen un id
            already_exists = Role.objects.filter(
            name=name, project_id=self.project_id).exclude(id=self.id).exists()
        else:    #crear roles, pues no tienen un id
            already_exists = Role.objects.filter(
            name=name, project_id=self.project_id).exists()

        if already_exists:
            raise forms.ValidationError(build_field_error(
                'name', 'Ya existe un rol con ese nombre'))

        #no pude ser un rol sin proyecto, porque son Default
        default_role = Role.objects.filter(
        name=name, project_id=None).exists()

        if default_role:
            raise forms.ValidationError(build_field_error(
                'name', 'Ya existe un rol por defecto con ese nombre'))

        return cleaned_data

class FormUserStoryType(forms.Form):
    """
    Formulario base para el modelo UserStoryType
    """
    name = forms.CharField(max_length=100, label='Nombre',
                           widget=widgets.TextInput())
    columns = forms.CharField(label='Columnas (Las columnas ingresadas iran entre To Do y Done)',
                              widget=widgets.TextInput(attrs={'placeholder': 'Ej: In Progress, Testing'}))

    def custom_clean_columns(self, columns):
        # Creo un array de los nombres de las columnas
        columns=columns.upper()
        final_columns = "TO DO," + columns + ",DONE"
        print (columns)
        print (final_columns)
        array_column = columns.split(',')

        array_column = [x.strip() for x in array_column]

        # Verifico que haya minimo dos columnas
        if len(array_column) < 1:
            raise forms.ValidationError(build_field_error(
                'columns', 'Debe ingresar al menos una columna'))

        array_column = final_columns.split(',')
        array_column = [x.strip() for x in array_column]

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
class FormCreateUserStory(forms.Form):
    """
    Formulario para crear una historia de usuario en un proyecto
    """
    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.fields['us_type'] = forms.ModelChoiceField(
            queryset=ProjectUseCase.filter_user_story_type_by_project(project_id), label='Tipo de Historia de Usuario',
            empty_label='Seleccione un tipo',
            widget=widgets.SelectInput()
        )
        self.fields['title'] = forms.CharField(max_length=100, label='Titulo',widget=widgets.TextInput())  # TITULO del US
        self.fields['description'] = forms.CharField(max_length=100, label='Descripcion',widget=widgets.TextInput())  # descripcion del US
        self.fields['business_value'] = forms.IntegerField( min_value=1, max_value=100 ,label='Valor de Negocio',widget=widgets.NumberInput())  # Valor de Negocio del US
        self.fields['technical_priority'] = forms.IntegerField(min_value=1, max_value=100 ,label='Prioridad Tecnica',widget=widgets.NumberInput())  # Prioridad Tecnica del US
        self.fields['estimation_time'] = forms.IntegerField(min_value=1, max_value=100 , label='Tiempo estimado',widget=widgets.NumberInput())  # Tiempo estimado del US
        self.fields['attachments'] = forms.FileField(
            required=False, label='Adjuntos', widget=widgets.FileInput(attrs={'multiple': True}))  # Adjuntos del US
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        already_exists = UserStory.objects.filter(
            title=title, project_id=self.project_id).exists()
        if already_exists:
            raise forms.ValidationError(build_field_error(
                'title', 'Ya existe una historia de usuario con ese nombre'))
        return cleaned_data

class FormCreateUserStoryPO(forms.Form):
    """
    Formulario para crear una historia de usuario en un proyecto
    """
    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.fields['us_type'] = forms.ModelChoiceField(
            queryset=ProjectUseCase.filter_user_story_type_by_project(project_id), label='Tipo de Historia de Usuario',
            empty_label='Seleccione un tipo',
            widget=widgets.SelectInput()
        )
        self.fields['title'] = forms.CharField(max_length=100, label='Titulo',widget=widgets.TextInput())  # TITULO del US
        self.fields['description'] = forms.CharField(max_length=100, label='Descripcion',widget=widgets.TextInput())  # descripcion del US
        self.fields['business_value'] = forms.IntegerField( min_value=1, max_value=100 ,label='Valor de Negocio',widget=widgets.NumberInput())  # Valor de Negocio del US
        self.fields['attachments'] = forms.FileField(
            required=False, label='Adjuntos', widget=widgets.FileInput(attrs={'multiple': True}))  # Adjuntos del US
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        already_exists = UserStory.objects.filter(
            title=title, project_id=self.project_id).exists()
        if already_exists:
            raise forms.ValidationError(build_field_error(
                'title', 'Ya existe una historia de usuario con ese nombre'))
        return cleaned_data


class ImportUserStoryTypeForm1(forms.Form):
    """
    Formulario para seleccionar un proyecto de donde importar los tipos de historia de usuario
    """

    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.fields['project'] = forms.ModelChoiceField(
            queryset=Project.objects.exclude(id=project_id),
            empty_label='Seleccione un proyecto',
            label='Proyecto', widget=widgets.SelectInput())

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project')

        amount_us_type = UserStoryType.objects.filter(project_id=project.id).count()
        if amount_us_type == 1:
            raise forms.ValidationError(build_field_error(
                'project', 'El proyecto seleccionado no tiene tipos de historia de usuario a importar'))
        return cleaned_data

class ImportUserStoryTypeForm2(forms.Form):
    """
    Formulario para seleccionar los tipos de historia de usuario a importar de un proyecto
    """

    def __init__(self, from_project_id, to_project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_project_id = from_project_id
        self.to_project_id = to_project_id
        self.fields['user_story_types'] = forms.ModelMultipleChoiceField(
           queryset=UserStoryType.objects.filter(project_id=from_project_id).exclude(name='Historia de Usuario'),
           label='Seleccione los tipos de US que desea importar', widget=forms.CheckboxSelectMultiple())

    def clean(self):
        cleaned_data = super().clean()
        user_story_types = cleaned_data.get('user_story_types')
        if not user_story_types:
            raise forms.ValidationError('Debe seleccionar al menos un tipo de historia de usuario')

        from_project = Project.objects.get(id=self.from_project_id)
        # Verificar si el proyecto destino tiene tipos de historia de usuario con el mismo nombre
        append_project_name = lambda us_type: f"{us_type.name} (importado {from_project.name})"
        already_exists = lambda us_type: UserStoryType.objects.filter(
            name=append_project_name(us_type), project_id=self.to_project_id).exists()

        no_import_user_story_type = list(filter(already_exists, user_story_types))
        import_user_story_type = list(set(user_story_types) - set(no_import_user_story_type))

        cleaned_data['user_story_types'] = import_user_story_type
        cleaned_data['no_import_user_story_types'] = no_import_user_story_type
        return cleaned_data

class ImportRoleForm1(forms.Form):
    """
    Formulario para seleccionar un proyecto de donde importar los roles
    """

    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.fields['project'] = forms.ModelChoiceField(
            queryset=Project.objects.exclude(id=project_id),
            empty_label='Seleccione un proyecto',
            label='Proyecto', widget=widgets.SelectInput())

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project')

        amount_role = Role.objects.filter(project_id=project.id).count()
        if amount_role == 0:
            raise forms.ValidationError(build_field_error(
                'project', 'El proyecto seleccionado no tiene roles a importar'))
        return cleaned_data

class FormEditUserStory(forms.Form):
    """
    Formulario para editar una historia de usuario en un proyecto
    """
    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.fields['us_type'] = forms.ModelChoiceField(
            queryset=ProjectUseCase.filter_user_story_type_by_project(project_id), label='Tipo de Historia de Usuario',
            empty_label='Seleccione un tipo',
            widget=widgets.SelectInput()
        )
        self.fields['title'] = forms.CharField(max_length=100, label='Titulo',widget=widgets.TextInput(attrs={'readonly': 'readonly'}))  # TITULO del US
        self.fields['description'] = forms.CharField(max_length=100, label='Descripcion',widget=widgets.TextInput())  # descripcion del US
        self.fields['business_value'] = forms.IntegerField( min_value=1, max_value=100 ,label='Valor de Negocio',widget=widgets.NumberInput())  # Valor de Negocio del US
        self.fields['technical_priority'] = forms.IntegerField(min_value=1, max_value=100 ,label='Prioridad Tecnica',widget=widgets.NumberInput())  # Prioridad Tecnica del US
        self.fields['estimation_time'] = forms.IntegerField(min_value=1, max_value=100 , label='Tiempo estimado',widget=widgets.NumberInput())  # Tiempo estimado del US

class FormCreateComment(forms.Form):
    """
    Formulario para crear un comentario de una us
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

class FormCreateHoliday(forms.Form):
    """
    Formulario para crear un feriado
    """
    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.fields['date'] = forms.DateField(initial=datetime.now())

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        already_exists = ProjectHoliday.objects.filter(
            project_id=self.project_id, date=date).exists()
        if already_exists:
            raise forms.ValidationError(build_field_error(
                'date', 'Ya existe este feriado'))
        return cleaned_data

class FormCreateTask(forms.Form):
    """
    Formulario para crear una Tarea de una us
    """
    def __init__(self, user_story_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_story_id = user_story_id
        self.fields['description'] = forms.CharField(max_length=100, label='Descripcion',widget=widgets.TextInput())
        self.fields['hours'] = forms.IntegerField(min_value=1, max_value=100 , label='Horas',widget=widgets.NumberInput())

class FormCreateAttachment(forms.Form):
    """
    Formulario para crear un comentario
    """
    def __init__(self, user_story_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_story_id = user_story_id
        self.fields['attachments'] = forms.FileField(
            required=False, label='Adjuntos', widget=widgets.FileInput(attrs={'multiple': True}))
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

