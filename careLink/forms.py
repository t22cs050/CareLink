from .models import Schedule, FamilyUser 
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Elder

# --- ユーザ登録フォーム
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = FamilyUser
        fields = (
            'username',
            'elder_code'
        )

    # --- ユーザー名の重複チェック
    def clean_username(self):
        # すでに登録されているユーザー名の確認
        username = self.cleaned_data['username']
        if FamilyUser.objects.filter(username=username).exists():
            raise ValidationError('このユーザー名は既に登録されています。別のユーザー名を選択してください。')
        
        return username

    # ---- elderコードのバリデーション
    def clean_elder_code(self):
        # elderコードがElderモデルに存在するか確認
        elder_code = self.cleaned_data['elder_code']
        if not Elder.objects.filter(elder_code=elder_code).exists():
            raise ValidationError('無効なelderコードです。')
        return elder_code

    # --- パスワードのバリデーション
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        # パスワード一致のチェック
        if password1 and password2 and password1 != password2:
            raise ValidationError('パスワードが一致しません。')
        
        # パスワードの複雑性チェック
        if len(password1) < 8:
            raise ValidationError('パスワードは少なくとも8文字以上である必要があります。')
        
        return password2
    
    # --- フォーム全体のバリデーション
    def clean(self):
        cleaned_data = super().clean()        
        return cleaned_data
    

# --- 行動登録フォーム
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['title', 'date', 'time', 'recurrence']  # 仮フィールド
        

    # # エフェクト画像一日につき一つまでしか登録出来ないようにする（管理者サイトからからはできちゃう）
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     date = cleaned_data.get('date')
    #     image = cleaned_data.get('image')

    #     # すでに同じ date に登録された Schedule が存在するか確認
    #     if date and image:  # date と image がフォームに入力されている場合のみチェック
    #         existing_schedule = Schedule.objects.filter(date=date, image__isnull=False).exists()
    #         if existing_schedule:
    #             raise ValidationError(
    #                 f"選択した日付 ({date}) には既に画像が登録されています。"
    #             )

    #     return cleaned_data



# --- 日付入力フォーム
class DateInputForm(forms.Form):
    date = forms.DateField(
        initial=timezone.now().date(),  # デフォルトで今日の日付を設定
        widget=forms.DateInput(attrs={'type': 'date'})
    )

# --- 画像登録フォーム
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = FamilyUser
        fields = ['image']