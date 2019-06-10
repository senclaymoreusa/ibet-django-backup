# Generated by Django 2.1.7 on 2019-06-10 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0016_merge_20190607_1414'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='depositchannel',
            options={'verbose_name': 'Deposit Channel', 'verbose_name_plural': 'Deposit Channels'},
        ),
        migrations.AlterModelOptions(
            name='withdrawchannel',
            options={'verbose_name': 'Withdraw Channel', 'verbose_name_plural': 'Withdraw Channels'},
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'SUCCESS'), (1, 'FAILED'), (2, 'PENDING'), (3, 'APPROVED'), (4, 'REJECTED')], default=2, verbose_name='Status'),
        ),
    ]
