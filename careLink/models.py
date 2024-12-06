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