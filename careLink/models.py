from django.db import models
from .randomGenerate import generate_unique_integer


class Elder(models.Model):
    # 5桁以上10桁未満の整数
    elder_id = models.IntegerField(unique=True)
    # 4桁の整数
    elder_code = models.IntegerField(unique=True)

    def save(self, *args, **kwargs):
        # elder_idを自動生成（5桁以上10桁未満）
        if not self.elder_id:
            self.elder_id = generate_unique_integer(
                Elder, 'elder_id', 10000, 999999999
            )
        # elder_codeを自動生成（4桁の整数）
        if not self.elder_code:
            self.elder_code = generate_unique_integer(
                Elder, 'elder_code', 1000, 9999
            )
        super().save(*args, **kwargs)  # 元のsaveメソッドを呼び出す


class Family(models.Model):
    # 5桁以上10桁未満の整数
    family_id = models.IntegerField(unique=True)
    # 4桁の整数
    elder_code = models.IntegerField(unique=True)
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=20)