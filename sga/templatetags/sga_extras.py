from django import template
from django.urls import resolve, Resolver404
import re

from projects.models import Project, Role, UserStoryType
from sprints.models import Sprint
from user_stories.models import UserStory

register = template.Library()

@register.simple_tag()
def is_active(request, pattern):
    """
    Retorna 'active' si la url de la request coincide con el patrón
    """
    if re.search(pattern, request.path):
        return 'active'
    return ''


@register.simple_tag()
def get_path_param(request, arg_name):
    """
    Retorna el valor de un parámetro de la url

    Ejemplo
    path = "/projects/<int:project_id>/roles"

    get_path_param(request, 'project_id') -> 1
    """
    kwargs = request.resolver_match.kwargs
    if arg_name in kwargs:
        return kwargs[arg_name]
    return None

@register.inclusion_tag( 'utils/breadcrumb.html', takes_context=True)
def breadcrumb(context):
    """
    Retorna una lista de tuplas (nombre, url) para el breadcrumb

    Ejemplo
    {% breadcrumb 'Proyectos' 'projects:list' 'Roles' 'projects:roles' %}
    """
    request = context['request']
    path = request.path

    names = {
        'projects': 'Proyecto',
        'user-story-type': 'Tipo de Historia de Usuario',
        'user-story': 'Historia de Usuario',
        'sprints': 'Sprint',
        'roles': 'Rol',
        'members': 'Miembro',
        'backlog': 'Backlog',
        'create': 'Creación',
        'edit': 'Edición',
        'import': 'Importación',
        'board': 'Tablero',
        'assign': 'Asignación',
    }
    get_name = {
        'projects': lambda x: Project.objects.get(pk=x).name,
        'user-story-type': lambda x: UserStoryType.objects.get(pk=x).name,
        'user-story': lambda x: UserStory.objects.get(pk=x).name,
        'backlog': lambda x: UserStory.objects.get(pk=x).code,
        'sprints': lambda x: Sprint.objects.get(pk=x).name,
        'roles': lambda x: Role.objects.get(pk=x).name,
    }
    breadcrumb = []
    while path:

        match = re.search(r'(?P<model_name>[\w-]+)/(?P<model_id>[\w-]+)/?', path)
        if not match:
            break
        path = path[match.end():]

        model_name = match.group('model_name')
        model_id = match.group('model_id')

        name = names[model_name] if model_name in names else model_name
        if model_id in ['create', 'edit', 'import', 'board', 'assign']:
            model_name_id = names[model_id]
        else:
            model_name_id = get_name[model_name](model_id) if model_name in get_name else model_id

        model_url = f'{model_name}/{model_id}'
        previous_path = breadcrumb[-1][1] if breadcrumb else ''

        model_list_url = f"{previous_path}/{model_name}"
        model_id_url = f"{previous_path}/{model_url}"
        breadcrumb.append((name, model_list_url, exists_path(model_list_url)))
        breadcrumb.append((model_name_id, model_id_url, exists_path(model_id_url)))
    if(path):
        path = path.replace('/', '')
        previous_path = breadcrumb[-1][1] if breadcrumb else ''
        name = names[path] if path in names else path
        breadcrumb.append((name, f'{previous_path}/{path}', True))
    return {
        'breadcrumb': breadcrumb,
    }

def exists_path(path):
    """
    Retorna True si existe alguna vista que coincida con el path
    """
    try:
        resolve(f"{path}/")
        return True
    except Resolver404:
        return False

