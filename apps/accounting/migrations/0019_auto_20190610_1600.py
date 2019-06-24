# Generated by Django 2.1.7 on 2019-06-10 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0018_merge_20190610_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.SmallIntegerField(choices=[(0, 'Deposit'), (1, 'Withdrawal'), (2, 'Bet Placed'), (3, 'Bet Settled'), (4, 'Transfer In'), (5, 'Transfer Out'), (6, 'Bonus'), (7, 'Adjustment')], default=0, verbose_name='Transaction Type'),
        ),
    ]
