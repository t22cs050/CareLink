from .models import Schedule, FamilyUser 
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.core.exceptions import ValidationError


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
        fields = ['title', 'date', 'time', 'recurrence','image']  # 仮フィールド
        
        
        
    # エフェクト画像一日につき一つまでしか登録出来ないようにする（管理者サイトからからはできちゃう）
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        image = cleaned_data.get('image')

        # すでに同じ date に登録された Schedule が存在するか確認
        if date and image:  # date と image がフォームに入力されている場合のみチェック
            existing_schedule = Schedule.objects.filter(date=date, image__isnull=False).exists()
            if existing_schedule:
                raise ValidationError(
                    f"選択した日付 ({date}) には既に画像が登録されています。"
                )

        return cleaned_data
    
    
        
        
        

# --- 日付入力フォーム
class DateInputForm(forms.Form):
    date = forms.DateField(
        initial=timezone.now().date(),  # デフォルトで今日の日付を設定
        widget=forms.DateInput(attrs={'type': 'date'})
    )