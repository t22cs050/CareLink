from .models import Schedule, FamilyUser 
from django import forms
from django.contrib.auth.forms import UserCreationForm

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