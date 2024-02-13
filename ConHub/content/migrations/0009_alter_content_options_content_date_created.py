# Generated by Django 5.0.1 on 2024-02-02 20:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0008_rename_linked_video_content_video_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ['-date_created']},
        ),
        migrations.AddField(
            model_name='content',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]