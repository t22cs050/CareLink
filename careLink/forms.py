from .models import Schedule, FamilyUser 
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

# --- ユーザ登録フォーム
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = FamilyUser
        fields = (
            'username',
            'elder_code'
        )

# --- 行動登録フォーム
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['title', 'date', 'recurrence']  # 仮フィールド

# --- 日付入力フォーム
class DateInputForm(forms.Form):
    date = forms.DateField(
        initial=timezone.now().date(),  # デフォルトで今日の日付を設定
        widget=forms.DateInput(attrs={'type': 'date'})
    )