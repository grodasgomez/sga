from django import forms

from users.models import Permission


class FormRoles(forms.Form):

    name_role = forms.CharField(max_length=100)  # nombre del rol
    description_role = forms.CharField(max_length=100)  # descripcion del rol
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(), widget=forms.CheckboxSelectMultiple())
