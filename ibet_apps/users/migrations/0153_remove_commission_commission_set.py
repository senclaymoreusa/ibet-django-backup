# Generated by Django 2.1.7 on 2019-09-30 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0152_auto_20190927_1459'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commission',
            name='commission_set',
        ),
    ]
