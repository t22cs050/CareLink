from django.db import models
from django.contrib.auth.models import AbstractUser
from .randomGenerate import generate_unique_integer
from pathlib import Path


class Elder(models.Model):
    # 5桁以上10桁未満の整数
    elder_id = models.IntegerField(unique=True, default='00000')
    # 4桁の整数
    elder_code = models.IntegerField(unique=True, default='0000')

    def save(self, *args, **kwargs):
        # elder_idを自動生成（5桁以上10桁未満）
        if not self.elder_id:
            self.elder_id = generate_unique_integer(
                Elder, 'elder_id', 10000, 999999999
            )
            print("is not elder_id")
        # elder_codeを自動生成（4桁の整数）
        if not self.elder_code:
            self.elder_code = generate_unique_integer(
                Elder, 'elder_code', 1000, 9999
            )
            print("is not elder_code")
        super().save(*args, **kwargs)  # 元のsaveメソッドを呼び出す


class FamilyUser(AbstractUser):
    elder_code = models.IntegerField(default='0000') # 4桁の整数
    REQUIRED_FIELDS = ['elder_code', ]
    image = models.ImageField(upload_to='schedule_images/', blank=True, null=True)  # 画像フィールド

    # 画像消すためのオーバーライド
    def delete(self,*args,**kwargs):
        image=self.image
        super().delete(*args,**kwargs)
        if image:
            Path(image.path).unlink(missing_ok=True)

# --- 行動管理DB定義
class Schedule(models.Model):
    RECURRING_CHOICES = [
        ('none', '繰り返さない'),
        ('daily', '日ごと'),
        ('weekly', '週ごと'),
        ('monthly', '月ごと'),
    ]

    title = models.CharField(max_length=100, default='', blank=True) # 行動名
    date = models.DateField() # 日付
    time = models.TimeField(blank=True, null=True) # 時刻
    recurrence = models.CharField(max_length=10, choices=RECURRING_CHOICES, default='none') # 繰り返し設定
    completion = models.BooleanField(default=False)             # 状態（T/F）
    sequence = models.IntegerField(default=1)                   # 行動順序
    silver_code = models.CharField(max_length=100, default='')  # 高齢者コード

    def __str__(self):
        return self.title
    

