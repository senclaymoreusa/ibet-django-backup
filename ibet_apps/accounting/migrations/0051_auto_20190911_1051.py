# Generated by Django 2.1.7 on 2019-09-11 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0050_auto_20190830_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depositchannel',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR'), (4, 'HKD'), (5, 'AUD'), (6, 'MYR'), (7, 'VND'), (8, 'MMK'), (9, 'XBT'), (10, 'NOK'), (11, 'SEK'), (12, 'GBP'), (13, 'EUR')], default=0, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='depositchannel',
            name='thirdParty_name',
            field=models.SmallIntegerField(choices=[(0, 'Help2Pay'), (1, 'LINEpay'), (2, 'AstroPay'), (3, 'Qaicash'), (4, 'AsiaPay'), (5, 'Paypal'), (6, 'Payzod'), (7, 'CirclePay'), (8, 'Fgate'), (9, 'ScratchCard'), (10, 'PaymentIQ')], default=2, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='channel',
            field=models.SmallIntegerField(choices=[(0, 'Help2Pay'), (1, 'LINEpay'), (2, 'AstroPay'), (3, 'Qaicash'), (4, 'AsiaPay'), (5, 'Paypal'), (6, 'Payzod'), (7, 'CirclePay'), (8, 'Fgate'), (9, 'ScratchCard'), (10, 'PaymentIQ')], default=0, verbose_name='Payment'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR'), (4, 'HKD'), (5, 'AUD'), (6, 'MYR'), (7, 'VND'), (8, 'MMK'), (9, 'XBT'), (10, 'NOK'), (11, 'SEK'), (12, 'GBP'), (13, 'EUR')], default=0, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR'), (4, 'HKD'), (5, 'AUD'), (6, 'MYR'), (7, 'VND'), (8, 'MMK'), (9, 'XBT'), (10, 'NOK'), (11, 'SEK'), (12, 'GBP'), (13, 'EUR')], default=0, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='thirdParty_name',
            field=models.SmallIntegerField(choices=[(0, 'Help2Pay'), (1, 'LINEpay'), (2, 'AstroPay'), (3, 'Qaicash'), (4, 'AsiaPay'), (5, 'Paypal'), (6, 'Payzod'), (7, 'CirclePay'), (8, 'Fgate'), (9, 'ScratchCard'), (10, 'PaymentIQ')], default=2, verbose_name='Name'),
        ),
    ]
