# Generated by Django 2.1.7 on 2019-11-09 01:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0036_gamebet_transaction_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamebet',
            name='transaction_id',
        ),
    ]
