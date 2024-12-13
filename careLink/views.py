from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, DeleteView
from .models import Elder, Family
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from . import mixins
from datetime import datetime
from .randomGenerate import generate_unique_integer


def login(request):
    return render(request, 'careLink/login.html')


class signUpElder(CreateView):
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


class signUpFamily(CreateView):
    model = Family
    fields = ('name', 'password')
    template_name = 'careLink/family_add.html'
    success_url = '/careLink/login'

    # 行動状況の確認
    def result(request):
        # クエリパラメータから日付情報を取得
        date_str = request.GET.get('date')
        selected_date = None

        if date_str:
            try:
                # 日付情報をパース
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = None  # パースエラー時はNoneに設定

        # 現在の月を取得
        month_current = datetime.now()

        # テンプレートにデータを渡す
        return render(request, 'careLink/result.html', {
            'selected_date': selected_date,
            'month_current': month_current,
        })

    # --- 月間カレンダーを表示するビュー ---
    class MonthCalendar(mixins.MonthCalendarMixin, TemplateView):
        
        template_name = 'careLink/result-calender.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            calendar_context = self.get_month_calendar()
            context.update(calendar_context)
            return context


