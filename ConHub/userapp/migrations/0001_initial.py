# Generated by Django 5.0.1 on 2024-02-04 13:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Userprofile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=300, null=True)),
                ('country', models.CharField(blank=True, max_length=300, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('fullname', models.CharField(blank=True, max_length=100, null=True)),
                ('username', models.CharField(default=1, max_length=50, null=True)),
                ('profile_image', models.ImageField(upload_to='profile')),
                ('activation_key', models.CharField(blank=True, max_length=300, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]