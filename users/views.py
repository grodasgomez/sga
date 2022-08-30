from multiprocessing import context
from django.shortcuts import render
import users.models

# Create your views here.
def agg_roles(request):
    #select * from sga_permission
    permissions = users.models.permission.objects.all()
    context = { "list_permissions" : permissions}
    #print ([x.name for x in permissions])
    return render(request, 'sga/agg_roles.html', context)