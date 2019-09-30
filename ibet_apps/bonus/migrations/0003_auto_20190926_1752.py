# Generated by Django 2.1.7 on 2019-09-27 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0002_userbonus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requirement',
            name='field_name',
            field=models.SmallIntegerField(choices=[(0, 'Deposit'), (1, 'Withdrawal'), (2, 'Bet Placed'), (3, 'Bet Settled'), (4, 'Transfer'), (5, 'Bonus'), (6, 'Adjustment'), (7, 'Commission')], default=0, verbose_name='Transaction Type'),
        ),
    ]
