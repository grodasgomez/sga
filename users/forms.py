from django import forms
import users.models



class FormRoles(forms.Form):
    name_role=forms.CharField(max_length=100) #nombre del rol
    description_role=forms.CharField( max_length=100) #descripcion del rol
    #sera de multiples opciones con un checkbox, las opciones son los permisos
    permissions=forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
