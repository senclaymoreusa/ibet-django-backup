# Generated by Django 2.1.7 on 2019-04-05 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0072_auto_20190405_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='contact_option',
            field=models.CharField(blank=True, choices=[('Email', 'Email'), ('SMS', 'SMS'), ('OMS', 'OMS'), ('Push_Notification', 'Push Notification')], max_length=6),
        ),
    ]
