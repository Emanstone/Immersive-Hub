# Generated by Django 5.0.1 on 2024-02-11 09:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0009_subscription_next_payment_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='paystack_id',
        ),
    ]