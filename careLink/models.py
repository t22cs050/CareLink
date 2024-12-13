from django.db import models


class Elder(models.Model):
    # 5桁以上10桁未満の整数
    elder_id = models.IntegerField()
    # 4桁の整数
    elder_code = models.IntegerField()


class Family(models.Model):
    # 5桁以上10桁未満の整数
    family_id = models.IntegerField()
    # 4桁の整数
    elder_code = models.IntegerField()
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=20)


# --- 行動管理DB定義
class Schedule(models.Model):
    RECURRING_CHOICES = [
        ('none', '繰り返さない'),
        ('daily', '日ごと'),
        ('weekly', '週ごと'),
        ('monthly', '月ごと'),
    ]

    title = models.CharField(max_length=100, default='') # 行動名
    date = models.DateField() # 日付
    recurrence = models.CharField(max_length=10, choices=RECURRING_CHOICES, default='none') # 繰り返し設定
    description = models.TextField(blank=True)      # 説明
    completion = models.BooleanField(default=False) # 状態（T/F）
    silver_code = models.CharField(max_length=100, default='')  # 高齢者コード

    def __str__(self):
        return self.title
