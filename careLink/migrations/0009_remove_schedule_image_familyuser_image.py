
# Generated by Django 5.1.4 on 2025-01-19 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careLink', '0008_remove_schedule_unique_image_per_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='image',
        ),
        migrations.AddField(
            model_name='familyuser',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='schedule_images/'),
        ),
    ]
