# Generated by Django 2.1.7 on 2019-09-27 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0055_merge_20190926_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.SmallIntegerField(choices=[(0, 'Deposit'), (1, 'Withdrawal'), (2, 'Bet Placed'), (3, 'Bet Settled'), (4, 'Transfer in'), (5, 'Transfer out'), (6, 'Bonus'), (7, 'Adjustment'), (8, 'Commission')], default=0, verbose_name='Transaction Type'),
        ),
    ]
