# Generated by Django 2.1.7 on 2019-09-27 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0052_merge_20190917_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depositchannel',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR'), (4, 'HKD'), (5, 'AUD'), (6, 'MYR'), (7, 'VND'), (8, 'MMK'), (9, 'XBT'), (10, 'EUR'), (11, 'NOK'), (12, 'GBP')], default=0, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR'), (4, 'HKD'), (5, 'AUD'), (6, 'MYR'), (7, 'VND'), (8, 'MMK'), (9, 'XBT'), (10, 'EUR'), (11, 'NOK'), (12, 'GBP')], default=0, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.SmallIntegerField(choices=[(0, 'Deposit'), (1, 'Withdrawal'), (2, 'Bet Placed'), (3, 'Bet Settled'), (4, 'Transfer'), (5, 'Bonus'), (6, 'Adjustment'), (7, 'Commission')], default=0, verbose_name='Transaction Type'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR'), (4, 'HKD'), (5, 'AUD'), (6, 'MYR'), (7, 'VND'), (8, 'MMK'), (9, 'XBT'), (10, 'EUR'), (11, 'NOK'), (12, 'GBP')], default=0, verbose_name='Currency'),
        ),
    ]
