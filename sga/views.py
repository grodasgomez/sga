
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def profile(request):
    print(request.user)
    return render(request, 'sga/profile.html')

@login_required()
def index(request):
    return render(request, 'sga/index.html')

# def project(request):
#     # context = { 'prueba' : prueba }
#     result = request.user
#     print("USUARIO", result.id)
#     #select * from users_project where user_id==result_id
#     prueba = users.models.project.objects.filter(user_id=result.id)
#     print("PROYECTO", prueba)
#     context={ "roles" : [] }
#     for role in prueba:
#         context["roles"].append(Project.models.Role.objects.get(id=role.role_id))
#     print("ROLES", context)
#     return render(request, 'sga/project.html', context)
