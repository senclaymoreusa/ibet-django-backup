# Generated by Django 2.1.7 on 2019-11-13 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0041_remove_gamebet_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamebet',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR'), (4, 'HKD'), (5, 'AUD'), (6, 'MYR'), (7, 'VND'), (8, 'MMK'), (9, 'XBT'), (10, 'EUR'), (11, 'NOK'), (12, 'GBP'), (20, 'UUD'), (13, 'TTC')], default=0, verbose_name='Currency'),
        ),
        migrations.AddField(
            model_name='gamebet',
            name='transaction_id',
            field=models.CharField(default='000', max_length=200, verbose_name='Transaction id'),
        ),
    ]
