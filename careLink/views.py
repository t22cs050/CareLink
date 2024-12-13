from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, CreateView, DeleteView, TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Elder, Family, Schedule
from .forms import ScheduleForm # 行動登録に用いるフォーム
from . import mixins            # カレンダー関連のクラスを定義したやつ

from datetime import timedelta, date

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
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)  # 一時的に保存
            recurrence = schedule.recurrence
            start_date = schedule.start_date

            # 繰り返しデータを生成
            if recurrence != 'none':
                for i in range(0, 365):  # 1年分の繰り返し
                    new_schedule = Schedule(
                        title=schedule.title,
                        start_date=start_date,
                        recurrence=schedule.recurrence
                    )
                    if recurrence == 'daily':
                        new_schedule.start_date = start_date + timedelta(days=i)
                    elif recurrence == 'weekly':
                        new_schedule.start_date = start_date + timedelta(weeks=i)
                    elif recurrence == 'monthly':
                        new_schedule.start_date = start_date.replace(day=1) + timedelta(days=30 * i)
                        new_schedule.start_date = new_schedule.start_date.replace(day=min(start_date.day, (new_schedule.start_date + timedelta(days=31)).day))

                    new_schedule.save()
            else:
                schedule.save()  # 繰り返さない場合はそのまま保存

            return redirect('schedule_list')
    else:
        form = ScheduleForm(initial={'start_date': date})  # 日付を初期値として設定
    return render(request, 'careLink/add_schedule.html', {'form': form, 'date': date})