from multiprocessing import context
from random import choices
from django.shortcuts import render
from django.http import HttpResponse

from users.models import Role
from .forms import FormRoles

# Create your views here.