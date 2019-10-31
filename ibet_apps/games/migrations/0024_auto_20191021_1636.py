# Generated by Django 2.1.7 on 2019-10-21 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0023_gdcasino_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gdcasino',
            name='cancelReason',
            field=models.SmallIntegerField(choices=[(0, 'None'), (1, 'Game round is cancelled.'), (2, 'Debit response timeout.'), (3, 'Abnormal bet is voided.'), (4, 'Betting time is ended'), (5, 'Debit reply is in wrong format.')], default=0),
        ),
    ]
