# Generated by Django 5.1.4 on 2024-12-27 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careLink', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='time',
            field=models.TimeField(blank=True),
        ),
    ]
