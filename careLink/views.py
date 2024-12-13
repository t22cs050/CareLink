from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView
from .models import Elder, Family
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .randomGenerate import generate_unique_integer


def login(request):
    return render(request, 'careLink/login.html')


class signInElder(CreateView):
    model = Elder
    fields = ()
    template_name = 'careLink/elder_add.html'
    success_url = '/careLink/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # セッションにelder_idとelder_codeがなければ生成して保存
        if 'elder_id' not in self.request.session:
            self.request.session['elder_id'] = generate_unique_integer(Elder, 'elder_id', 10000, 999999999)
        if 'elder_code' not in self.request.session:
            self.request.session['elder_code'] = generate_unique_integer(Elder, 'elder_code', 1000, 9999)

        # セッションからelder_idとelder_codeを取得してコンテキストに追加
        context['elder_id'] = self.request.session['elder_id']
        context['elder_code'] = self.request.session['elder_code']

        return context

    def form_valid(self, form):
        # セッションからelder_idとelder_codeを取得してセット
        form.instance.elder_id = self.request.session.pop('elder_id')
        form.instance.elder_code = self.request.session.pop('elder_code')

        return super().form_valid(form)


class signInFamily(CreateView):
    model = Family
    fields = ('name', 'password')
    template_name = 'careLink/family_add.html'
    success_url = '/careLink/login'
