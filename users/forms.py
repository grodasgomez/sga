from django import forms
import users.models



class FormRoles(forms.Form):
    #tomamos todos los permisos de la base de datos
    permissions_db=users.models.permission.objects.all()
    CHOICES=[]

    for perm in permissions_db:
        #agregamos el nombre y el id de cada permiso en una lista que usaremos para el checklist
        CHOICES.append((perm.id,perm.name))
        
    name_role=forms.CharField(max_length=100) #nombre del rol
    description_role=forms.CharField( max_length=100) #descripcion del rol
    #sera de multiples opciones con un checkbox, las opciones son los permisos
    permissions=forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())
