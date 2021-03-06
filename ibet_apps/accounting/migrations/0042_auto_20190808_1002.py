# Generated by Django 2.1.7 on 2019-08-08 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0041_auto_20190716_1516'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='depositchannel',
            name='thridParty_id',
        ),
        migrations.RemoveField(
            model_name='depositchannel',
            name='thridParty_name',
        ),
        migrations.RemoveField(
            model_name='withdrawchannel',
            name='thridParty_id',
        ),
        migrations.RemoveField(
            model_name='withdrawchannel',
            name='thridParty_name',
        ),
        # migrations.AddField(
        #     model_name='depositchannel',
        #     name='id',
        #     field=models.AutoField(auto_created=True, default=0, primary_key=True, serialize=False, verbose_name='ID'),
        #     preserve_default=False,
        # ),
        # migrations.AddField(
        #     model_name='withdrawchannel',
        #     name='id',
        #     field=models.AutoField(auto_created=True, default=0, primary_key=True, serialize=False, verbose_name='ID'),
        #     preserve_default=False,
        # ),
        migrations.AlterField(
            model_name='transaction',
            name='channel',
            field=models.SmallIntegerField(choices=[(0, 'Help2Pay'), (1, 'LINEpay'), (2, 'AstroPay'), (3, 'Qaicash'), (4, 'AsiaPay'), (5, 'Paypal'), (6, 'Payzod'), (7, 'CirclePay'), (8, 'Fgate')], default=0, verbose_name='Payment'),
        ),
    ]
