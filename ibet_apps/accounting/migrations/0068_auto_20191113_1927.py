# Generated by Django 2.1.7 on 2019-11-14 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0067_merge_20191113_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Success'), (1, 'Failed'), (2, 'Created'), (3, 'Pending'), (4, 'Approved'), (5, 'Canceled'), (6, 'Completed'), (7, 'Resent'), (8, 'Rejected'), (9, 'Review')], default=2, verbose_name='Status'),
        ),
    ]
