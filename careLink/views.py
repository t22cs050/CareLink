from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, CreateView, DeleteView, TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db import transaction

from .models import Elder, Family, Schedule
from .forms import ScheduleForm # 行動登録に用いるフォーム
from . import mixins            # カレンダー関連のクラスを定義したやつ

from datetime import timedelta, date
from dateutil.relativedelta import relativedelta # pip install python-dateutil 

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
    existing_schedules = Schedule.objects.filter(date=date) # その日付のスケジュールを取得
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            # バリデーションエラーを確認
            print("Form is valid")
            print(form.cleaned_data)
            
            try:
                with transaction.atomic():
                    if schedule.recurrence != 'none':
                        # より効率的な繰り返しスケジュール生成
                        schedules_to_create = []
                        for i in range(12):  # 1年分ではなく、12回の繰り返しに制限
                            if schedule.recurrence == 'daily':
                                new_date = schedule.date + timedelta(days=i)
                            elif schedule.recurrence == 'weekly':
                                new_date = schedule.date + timedelta(weeks=i)
                            elif schedule.recurrence == 'monthly':
                                new_date = schedule.date + relativedelta(months=i)
                            
                            schedules_to_create.append(Schedule(
                                title=schedule.title,
                                date=new_date,
                                recurrence=schedule.recurrence,
                                description=schedule.description,
                                completion=False,
                                silver_code=schedule.silver_code
                            ))
                        
                        # バルクインサート
                        Schedule.objects.bulk_create(schedules_to_create)
                    else:
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
        form = ScheduleForm(initial={'date': date})
    
    return render(request, 'careLink/add_schedule.html', {
        'form': form, 
        'date': date,
        'existing_schedules': existing_schedules
    })