# Generated by Django 5.1.4 on 2024-12-27 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("careLink", "0006_elder_elder_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="elder",
            name="elder_name",
            field=models.CharField(
                default=models.IntegerField(default="0000", unique=True), max_length=10
            ),
        ),
    ]
