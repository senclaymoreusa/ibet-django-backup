# Generated by Django 2.1.7 on 2019-10-01 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0053_auto_20191001_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='supplier',
        ),
    ]
