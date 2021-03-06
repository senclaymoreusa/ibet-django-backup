# Generated by Django 2.1.7 on 2019-06-06 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0014_auto_20190605_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payer_id',
            field=models.CharField(default=0, max_length=100),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'SUCCESS'), (1, 'FAILED'), (2, 'CREATED'), (3, 'PENDING'), (4, 'APPROVED'), (5, 'REJECTED'), (6, 'COMPLETED')], default=1, verbose_name='Status'),
        ),
    ]
