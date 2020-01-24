# Generated by Django 2.1.7 on 2020-01-09 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0080_merge_20200108_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='channel',
            field=models.SmallIntegerField(choices=[(0, 'Help2Pay'), (1, 'LINEpay'), (2, 'AstroPay'), (3, 'Qaicash'), (4, 'AsiaPay'), (5, 'Paypal'), (6, 'Payzod'), (7, 'CirclePay'), (8, 'Fgate'), (9, 'ScratchCard'), (10, 'PaymentIQ'), (11, 'Local Bank Transfer')], default=None, null=True, verbose_name='Payment'),
        ),
    ]
