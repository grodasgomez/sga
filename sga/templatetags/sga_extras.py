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