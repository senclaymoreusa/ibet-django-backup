# Generated by Django 2.1.15 on 2020-01-08 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0076_auto_20191212_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depositchannel',
            name='max_amount',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Max Amount'),
        ),
        migrations.AlterField(
            model_name='depositchannel',
            name='min_amount',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Min Amount'),
        ),
        migrations.AlterField(
            model_name='depositchannel',
            name='new_user_volume',
            field=models.DecimalField(decimal_places=4, default=100, max_digits=20),
        ),
        migrations.AlterField(
            model_name='depositchannel',
            name='transaction_fee',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=20, verbose_name='Transaction Fee'),
        ),
        migrations.AlterField(
            model_name='depositchannel',
            name='transaction_fee_per',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=20, verbose_name='Transaction Fee Percentage'),
        ),
        migrations.AlterField(
            model_name='depositchannel',
            name='volume',
            field=models.DecimalField(decimal_places=4, default=100, max_digits=20),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=4, max_digits=10, verbose_name='Apply Amount'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='channel',
            field=models.SmallIntegerField(choices=[(0, 'Help2Pay'), (1, 'LINEpay'), (2, 'AstroPay'), (3, 'Qaicash'), (4, 'AsiaPay'), (5, 'Paypal'), (6, 'Payzod'), (7, 'CirclePay'), (8, 'Fgate'), (9, 'ScratchCard'), (10, 'PaymentIQ'), (11, 'Local Bank Transfer')], default=0, null=True, verbose_name='Payment'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='max_amount',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Max Amount'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='min_amount',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Min Amount'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='new_user_volume',
            field=models.DecimalField(decimal_places=4, default=100, max_digits=20),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='transaction_fee',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=20, verbose_name='Transaction Fee'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='transaction_fee_per',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=20, verbose_name='Transaction Fee Percentage'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='volume',
            field=models.DecimalField(decimal_places=4, default=100, max_digits=20),
        ),
    ]
