# Generated by Django 2.1.7 on 2019-05-14 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20190514_1237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='depositchannel',
            name='user_id',
        ),
        migrations.RemoveField(
            model_name='withdrawchannel',
            name='user_id',
        ),
    ]
