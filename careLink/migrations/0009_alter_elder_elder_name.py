# Generated by Django 5.1.4 on 2025-01-22 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("careLink", "0008_alter_elder_elder_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="elder",
            name="elder_name",
            field=models.CharField(default="ユーザー", max_length=10),
        ),
    ]
