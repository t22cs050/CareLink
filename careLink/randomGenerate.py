import random

"""
指定されたモデルの指定フィールドにユニークな整数を生成。
:param model: モデルクラス
:param field_name: フィールド名
:param min_value: 最小値
:param max_value: 最大値
:return: ユニークな整数
"""


def generate_unique_integer(model, field_name, min_value, max_value):
    while True:
        value = random.randint(min_value, max_value)
        if not model.objects.filter(**{field_name: value}).exists():
            return value
