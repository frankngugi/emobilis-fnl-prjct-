# Generated by Django 5.0.3 on 2024-04-11 13:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_remove_video_caption_video_description_video_details_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='images',
            name='date',
            field=models.DateField(default=datetime.date, verbose_name='date'),
        ),
        migrations.AddField(
            model_name='media',
            name='date_created',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='is_phone_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='video',
            name='date',
            field=models.DateField(default=datetime.date, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='images',
            name='image',
            field=models.ImageField(default='Default description', upload_to='image/%y'),
        ),
    ]
