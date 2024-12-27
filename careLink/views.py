from django.views.generic import ListView, CreateView, DeleteView, TemplateView
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db.models import Max
from django.template.loader import render_to_string

from .models import Elder, Schedule
from .forms import ScheduleForm            # 行動登録に用いるフォーム
from .forms import UserRegistrationForm    # ユーザ登録に用いるフォーム 
from .forms import DateInputForm
from . import mixins # カレンダー関連のクラスを定義したやつ

from datetime import timedelta, date, datetime, timezone
from dateutil.relativedelta import relativedelta # pip install python-dateutil 
from .randomGenerate import generate_unique_integer

import json


# --- ログインview
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('family/schedule')  # ログイン後のリダイレクト先
        else:
            # エラーメッセージの表示
            return render(request, 'careLink/login.html', {'error': 'Invalid credentials or elder code.'})
    
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


# --- 家族側sginup画面
class signUpFamily(CreateView):
    fields = ('name', 'password')
    template_name = 'careLink/family_add.html'
    success_url = '/careLink/login'
    def register(request):
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)

            if form.is_valid():
                # DBにelder_codeが存在する場合登録が完了する
                if form.is_valid() and Elder.objects.filter(elder_code=form.cleaned_data.get('elder_code')).exists():
                    user = form.save()
                    return redirect('login')
                
                # 存在しなければエラーを返す
                else:
                    form.add_error('elder_code', 'Invalid elder code.')
        else:
            form = UserRegistrationForm()
        return render(request, 'careLink/family_add.html', {'form': form})


# --- 行動状況の確認
def result_view(request):
    form = DateInputForm()
    today = datetime.today()  # 今日の日付を取得
    schedules = Schedule.objects.filter(date=today)  # 今日のスケジュールを取得
    return render(request, 'careLink/result.html', {'form': form, 'schedules': schedules})

# --- 行動状況の取得を行う関数
def get_schedules(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        results = Schedule.objects.filter(date=selected_date) # 検索
        schedule_data = [
            {
                'title': item.title,
                'completion': '完了' if item.completion else '未完了'
            }
            for item in results
        ]
        return JsonResponse(schedule_data, safe=False)

# --- 月間カレンダーを表示するビュー
class MonthCalendar(mixins.MonthCalendarMixin, TemplateView):
    
    template_name = 'careLink/result-calender.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)
        return context


# --- 月間カレンダーを表示するビュー ---
class MonthCalendar(mixins.MonthCalendarMixin, TemplateView):
    
    template_name = 'careLink/calender.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)
        return context


# --- 行動登録画面
def add_schedule(request, date):
    existing_schedules = Schedule.objects.filter(date=date).order_by('sequence')  # その日のスケジュールを取得
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            max_sequence = Schedule.objects.filter(date=date).aggregate(Max('sequence'))['sequence__max'] # max(順序)を取得 
            print(max_sequence)     
            
            try:
                with transaction.atomic():
                    if schedule.recurrence != 'none':
                        # --- 繰り返しスケジュール生成
                        schedules_to_create = []
                        for i in range(12):  # 12回の繰り返す（要検討）
                            if schedule.recurrence == 'daily':
                                new_date = schedule.date + timedelta(days=i)
                            elif schedule.recurrence == 'weekly':
                                new_date = schedule.date + timedelta(weeks=i)
                            elif schedule.recurrence == 'monthly':
                                new_date = schedule.date + relativedelta(months=i)
                            
                            schedules_to_create.append(Schedule(
                                title=schedule.title,
                                date=new_date,
                                sequence = (max_sequence or 0) + 1,
                                recurrence=schedule.recurrence,
                                completion=False,
                            ))
                        
                        Schedule.objects.bulk_create(schedules_to_create) # バルクインサート
                    else:
                        schedule.sequence = (max_sequence or 0) + 1
                        schedule.save()
                
                messages.success(request, 'スケジュールを正常に登録しました。')
                render(request, 'careLink/add_schedule.html', {
                    'form': form, 
                    'date': date,
                    'existing_schedules': existing_schedules
                    })
            
            except Exception as e:
                messages.error(request, f'エラーが発生しました: {str(e)}')    
    else:
        form = ScheduleForm(initial={'date': date}) # 日付を初期値として設定
    
    return render(request, 'careLink/add_schedule.html', {
        'form': form, 
        'date': date,
        'existing_schedules': existing_schedules
    })

# --- 行動順序を変更する関数
def save_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = data.get('order', [])
        
        # 順序を更新
        for index, schedule_id in enumerate(order):
            Schedule.objects.filter(id=schedule_id).update(sequence=index + 1)
        print('save!')
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)

# --- 登録データを削除する関数
def delete_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('schedule_id')
            schedule = Schedule.objects.get(id=schedule_id)
            schedule.delete()  # スケジュールを削除
            print('delete!')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '無効なリクエストです。'})