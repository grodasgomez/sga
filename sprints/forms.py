from django import forms

from sprints.models import Sprint
from sga import widgets

class SprintStartForm(forms.Form):
    """
    Formulario para iniciar un sprint
    
    """