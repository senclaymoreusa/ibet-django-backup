# Generated by Django 2.1.7 on 2019-09-04 03:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0131_auto_20190903_2023'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamerequestsmodel',
            name='playname',
        ),
    ]
