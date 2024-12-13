from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView
from .models import Elder, Family
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404


def login(request):
    return render(request, 'careLink/login.html')


class signInElder(CreateView):
    model = Elder
    fields = ()
    template_name = 'careLink/elder_add.html'
    success_url = '/careLink/login'


class signInFamily(CreateView):
    model = Family
    fields = ('name', 'password')
    template_name = 'careLink/family_add.html'
    success_url = '/careLink/login'

def result_view(request):
    return render(request,'careLink/result.html')



