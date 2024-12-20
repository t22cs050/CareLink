from .models import Schedule 
from django import forms

# --- 行動登録フォーム
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['title', 'date', 'recurrence']  # 仮フィールド