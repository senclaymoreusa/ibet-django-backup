# Generated by Django 2.1.7 on 2019-08-19 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0044_auto_20190813_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depositchannel',
            name='thirdParty_name',
            field=models.SmallIntegerField(choices=[(0, 'Help2Pay'), (1, 'LINEpay'), (2, 'AstroPay'), (3, 'Qaicash'), (4, 'AsiaPay'), (5, 'Paypal'), (6, 'Payzod'), (7, 'CirclePay'), (8, 'Fgate'), (9, 'ScratchCard')], default=2, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='channel',
            field=models.SmallIntegerField(choices=[(0, 'Help2Pay'), (1, 'LINEpay'), (2, 'AstroPay'), (3, 'Qaicash'), (4, 'AsiaPay'), (5, 'Paypal'), (6, 'Payzod'), (7, 'CirclePay'), (8, 'Fgate'), (9, 'ScratchCard')], default=0, verbose_name='Payment'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='order_id',
            field=models.CharField(default=0, max_length=200, verbose_name='Order ID'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.CharField(default=0, max_length=200, verbose_name='Transaction ID'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='thirdParty_name',
            field=models.SmallIntegerField(choices=[(0, 'Help2Pay'), (1, 'LINEpay'), (2, 'AstroPay'), (3, 'Qaicash'), (4, 'AsiaPay'), (5, 'Paypal'), (6, 'Payzod'), (7, 'CirclePay'), (8, 'Fgate'), (9, 'ScratchCard')], default=2, verbose_name='Name'),
        ),
    ]
