from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from projects.forms import FormCreateProject

from projects.models import Project, ProjectStatus
from projects.usecase import ProjectUseCase


# Create your views here.
class ProjectView(LoginRequiredMixin, View):
    def get(self, request):
        data = Project.objects.all()
        context = {
            'projects': data
        }
        return render(request, 'projects/index.html', context)


class ProjectCreateView(LoginRequiredMixin, View):
    form_class = FormCreateProject

    def get(self, request):
        form = self.form_class()
        return render(request, 'projects/create.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.create_project(**cleaned_data)
            messages.success(request, 'Proyecto creado correctamente')
            
            return HttpResponseRedirect('/projects')
        return render(request, 'projects/create.html', {'form': form})
