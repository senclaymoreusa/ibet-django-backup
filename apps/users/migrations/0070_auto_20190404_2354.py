# Generated by Django 2.1.7 on 2019-04-05 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0069_auto_20190404_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='contact_option',
            field=models.CharField(choices=[('Email', 'Email'), ('SMS', 'SMS'), ('OMS', 'OMS'), ('Push_Notification', 'Push Notification')], max_length=6),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='currency',
            field=models.CharField(choices=[('usd', 'USD'), ('eur', 'EUR'), ('jpy', 'JPY'), ('cny', 'CNY'), ('hkd', 'HKD'), ('aud', 'AUD')], max_length=30),
        ),
    ]