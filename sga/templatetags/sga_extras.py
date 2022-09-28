from django import template
import re

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

@register.simple_tag(takes_context=True)
def breadcrumb(context):
    """
    Retorna una lista de tuplas (nombre, url) para el breadcrumb

    Ejemplo
    {% breadcrumb 'Proyectos' 'projects:list' 'Roles' 'projects:roles' %}
    """
    request = context['request']
    path = request.path

    breadcrumb = []
    while path:

        match = re.search(r'(?P<model_name>[\w-]+)/(?P<model_id>[\w-]+)/?', path)
        print(match)
        if not match:
            break
        path = path[match.end():]
        model_name = match.group('model_name')
        model_id = match.group('model_id')
        model_name_id = f'{model_name}-{model_id}'
        model_url = f'{model_name}/{model_id}'
        previous_path = breadcrumb[-1][1] if breadcrumb else ''

        breadcrumb.append((model_name, f"{previous_path}/{model_name}"))
        breadcrumb.append((model_name_id, f"{previous_path}/{model_url}"))
    if(path):
        previous_path = breadcrumb[-1][1] if breadcrumb else ''
        breadcrumb.append((path, f'{previous_path}/{path}'))
    return " | ".join([f'<a href="{url}">{name}</a>' for name, url in breadcrumb])
