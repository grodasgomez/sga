from multiprocessing import context
from random import choices
from django.shortcuts import render
from django.http import HttpResponse
import users.models
from .forms import FormRoles

# Create your views here.
def agg_roles(request):
    isRoleSave=0 #variable para saber si se guardo o no algo recientemente
    #si ocurrio un envio de informacion POST

    if request.method=="POST": 
        formRolPost=FormRoles(request.POST) #creamos un form con los datos cargados
        
        if formRolPost.is_valid(): #vemos si es valido
            formRolNew=formRolPost.cleaned_data #tomamos los datos
            print ("form enviado")
            print(formRolNew)
            oldRole=users.models.role.objects.all().filter(name=formRolNew['name_role']) #vemos si hay un rol en la bd con ese nombre
            if (len(oldRole)==0):
                newRole=users.models.role(name=formRolNew['name_role'],description=formRolNew['description_role']) #creamos un rol
                newRole.save() #guardamos el rol en bd

                for perm in formRolNew['permissions']: #veremos cada permiso
                    #tomamos de la bd cada permiso con el id correspondiente
                    permission_to_role=users.models.permission.objects.get(id=perm)
                    #agregamos el permiso al rol nuevo
                    newRole.permissions.add(permission_to_role)

                isRoleSave=1 #se guardo un rol
            else:
                isRoleSave=2 #el rol ya existe
    #form vacio para el template
    #tomamos todos los permisos de la base de datos
    permissions_db=users.models.permission.objects.all()
    
    CHOICES=[]

    for perm in permissions_db:
        #agregamos el nombre y el id de cada permiso en una lista que usaremos para el checklist
        CHOICES.append((perm.id,perm.name))

    print (CHOICES)
    formRol = FormRoles()
    formRol.fields['permissions'].choices=CHOICES #agregamos los permisos al form
    #enviamos el form vacio y el numero que indica si se cargo un rol o no
    return render(request, 'agg_roles.html', {'formRol': formRol,'isRoleSave':isRoleSave}) 