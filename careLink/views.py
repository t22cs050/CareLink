from django.views.generic import ListView, CreateView, DeleteView, TemplateView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db.models import Max
from django.template.loader import render_to_string
from django.conf import settings

from .models import Elder, Schedule, FamilyUser
from .forms import ScheduleForm            # 行動登録に用いるフォーム
from .forms import UserRegistrationForm    # ユーザ登録に用いるフォーム 
from .forms import ImageUploadForm
from .forms import DateInputForm

from . import mixins # カレンダー関連のクラスを定義したやつ
from django.views import View

from datetime import timedelta, date, datetime, timezone
from dateutil.relativedelta import relativedelta # pip install python-dateutil 
from .randomGenerate import generate_unique_integer
import requests
import json


# --- ログインview
def user_login(request):
    # クッキーに高齢者のログイン情報があればURLを変更する
    if isSignUpedElder(request):
        return redirect('elder/home')

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
    
    # すべての条件に合致しない場合の処理（例えば、GETリクエストの場合）
    return render(request, 'careLink/login.html')


def get_elder_from_cookie(request):
    """
    クッキーからElderIdとElderCodeを取得する関数。
    :param request: HttpRequestオブジェクト
    :return: elder_idとelder_codeのタプル（存在しない場合はNone, None）
    """
    if 'elder_id' in request.COOKIES:
        print("クッキー、あります")
    elder_id = request.COOKIES.get('elder_id')
    elder_code = request.COOKIES.get('elder_code')
    print(f"elder_id: {elder_id}, elder_code: {elder_code}")  # デバッグ用出力
    return elder_id, elder_code


def isSignUpedElder(request):
    elder_id, elder_code = get_elder_from_cookie(request)
    return (elder_id and elder_code)


class signUpElder(CreateView):
    model = Elder
    fields = ()
    template_name = 'careLink/elder_add.html'
    success_url = '/careLink/elder/home'

    # アクセスするときに呼び出される
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
        # print("get_context_data")        
        
        return context
    
    # データベースに保存
    def form_valid(self, form):
        # セッションからelder_idとelder_codeを取得してセット
        id = self.request.session.pop('elder_id')
        form.instance.elder_id = id
        code = self.request.session.pop('elder_code')
        form.instance.elder_code = code

        # データベースに保存
        form.instance.save()

        # Cookie に elder_id と elder_code を保存
        response = super().form_valid(form)
        response.set_cookie('elder_id', form.instance.elder_id, max_age=60*60)
        response.set_cookie('elder_code', form.instance.elder_code, max_age=60*60)

        return response


# --- 家族側sginup画面
class signUpFamily(CreateView):
    fields = ('name', 'password')
    template_name = 'careLink/family_add.html'
    success_url = '/careLink/user_login'
    def register(request):
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)

            if form.is_valid():
                # DBにelder_codeが存在する場合登録が完了する
                if form.is_valid() and Elder.objects.filter(elder_code=form.cleaned_data.get('elder_code')).exists():
                    user = form.save()
                    return redirect('/careLink/login')
                
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
    elder_code = request.user.elder_code # elder_codeを取得
    schedules = Schedule.objects.filter(date=today, silver_code=elder_code)  # 今日のスケジュールを取得
    return render(request, 'careLink/result.html', {'form': form, 'schedules': schedules})

# --- 行動状況の取得を行う関数
def get_schedules(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        elder_code = request.user.elder_code # elder_codeを取得
        results = Schedule.objects.filter(date=selected_date, silver_code=elder_code) # 検索
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
    elder_code = request.user.elder_code # ログインしているユーザの情報を取得
    existing_schedules = Schedule.objects.filter(date=date, silver_code=elder_code).order_by('sequence')  # その日のスケジュールを取得
    image_form = ImageUploadForm()
    form = ScheduleForm(initial={'date': date}) # 日付を初期値として設定
    if request.method == 'POST':
        form = ScheduleForm(request.POST,request.FILES)
        # --- スケジュールの変更がpostされた場合
        if 'schedule_submit' in request.POST:
            if form.is_valid():
                schedule = form.save(commit=False)
                max_sequence = Schedule.objects.filter(date=date, silver_code=elder_code).aggregate(Max('sequence'))['sequence__max'] # max(順序)を取得    
                
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
                                    silver_code = elder_code,
                                ))
                            
                            Schedule.objects.bulk_create(schedules_to_create) # バルクインサート
                        else:
                            schedule.sequence = (max_sequence or 0) + 1
                            schedule.silver_code = elder_code
                            schedule.save()
                    
                    messages.success(request, 'スケジュールを正常に登録しました。')
                    render(request, 'careLink/add_schedule.html', {
                        'form': form, 
                        'date': date,
                        'existing_schedules': existing_schedules
                        })
                
                except Exception as e:
                    messages.error(request, f'エラーが発生しました: {str(e)}')
        
        # --- 画像がpostされた場合
        elif 'image_submit' in request.POST:
            user = FamilyUser.objects.get(id=request.user.id)
            image_form = ImageUploadForm(request.POST, request.FILES, instance=user)
            if image_form.is_valid():
                image_form.save()
                messages.success(request, '画像がアップロードされました。')
        
    return render(request, 'careLink/add_schedule.html', {
        'form': form, 
        'date': date,
        'existing_schedules': existing_schedules,
        'image_form': image_form,
    })

# --- 登録した画像の削除
def delete_image(request):
    if request.user.image:
        request.user.image.delete()  # ファイルを削除
        request.user.image = None    # フィールドをクリア
        request.user.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def elderHome(request):

    if (request.method == 'POST'):
        # データの処理
        result = {'データを受け取りました'}
        return JsonResponse(result)

    today = datetime.today()
    
    elder_id = request.COOKIES.get('elder_id')
    elder_code = request.COOKIES.get('elder_code')
    print(f"Received elder_code: {elder_code}")  # デバッグ用
    if elder_code:
        # elder_code に基づいてスケジュールをフィルタリング
        schedules = Schedule.objects.filter(silver_code=elder_code, date=today).order_by('date')
        try:
            # elder_code に基づいて Elder インスタンスを取得
            elder = Elder.objects.get(elder_code=elder_code)
        except Elder.DoesNotExist:
            elder = None
    else:
        schedules = []
        elder = None
    print(f"Schedules: {schedules}")  # デバッグ用
    print(f"elder:{elder}") # デバッグ用
    
    return render(request, 'careLink/elder_home.html', {'schedules': schedules, 'elder': elder, 'elder_code':elder_code})


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
            print('delete:', schedule)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '無効なリクエストです。'})


# --- 達成/未達成が更新された場合
def update_schedule(request):
    if request.method == 'POST':
        try:
            # JSON データをパース
            data = json.loads(request.body)
            index = data.get('index')
            completion = data.get('completion')

            today = datetime.today()
            elder_code = request.COOKIES.get('elder_code')

            # 該当するスケジュールを取得して保存
            schedule = Schedule.objects.filter(silver_code=elder_code, date=today)[index]
            schedule.completion = completion
            schedule.save()

            # すべてのスケジュールが達成された場合はエフェクトを表示
            new_schedule = Schedule.objects.filter(silver_code=elder_code, date=today)
            if all(schedule.completion for schedule in new_schedule):
                print("return effect!")
                return redirect("/careLink/elder/effect")
            
            # 更新後のデータを返す
            return JsonResponse({
                'id': schedule.id,
                'title': schedule.title,
                'completion': schedule.completion,
            })

        except (Schedule.DoesNotExist, IndexError, KeyError):
            return JsonResponse({'error': 'Invalid data or schedule not found'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)   

# --- エフェクト画面
class AllCompleteEffect(TemplateView):
    def get(self,request):
        
        # クッキーから elder_code を取得
        elder_code = request.COOKIES.get('elder_code')
        
        # elder_code に基づいてスケジュールを取得
        if elder_code:
            image=FamilyUser.objects.get(elder_code=elder_code).image
        else:
            image = []  # elder_code がない場合は空のリスト
        print("aaaaaaaa", image)
        return render(request,"careLink/all_complete_effect.html",{"image":image,"MEDIA_URL": settings.MEDIA_URL,})

