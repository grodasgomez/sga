
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import users.models

def profile(request):
    print(request.user)
    return render(request, 'sga/profile.html')

@login_required()
def index(request):
    return render(request, 'sga/index.html')

def project(request):
    # context = { 'prueba' : prueba }
    result = request.user
    print("USUARIO", result.id)
    #select * from users_project where user_id==result_id
    prueba = users.models.project.objects.filter(user_id=result.id)
    print("PROYECTO", prueba)
    context={ "roles" : [] }
    for role in prueba:
        context["roles"].append(users.models.Role.objects.get(id=role.role_id))
    print("ROLES", context)
    return render(request, 'sga/project.html', context)


def list_users(request):
    #select * from sga_users
    CustomUsers = users.models.CustomUser.objects.all()
    #context guardara por cada usuario su info de CuntomUser y su rol
    context = { "user_list_with_roles" :  [] }
    for user in CustomUsers:
        roles = []
        user_roles = users.models.project.objects.filter(user_id=user.id)
        for role in user_roles:
            roles.append(users.models.Role.objects.get(id=role.role_id))

        context["user_list_with_roles"].append({"user":user,"roles":roles})

    return render(request, 'sga/users.html', context)