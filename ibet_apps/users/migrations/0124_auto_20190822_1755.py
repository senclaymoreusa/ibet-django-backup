# Generated by Django 2.1.7 on 2019-08-23 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0123_auto_20190819_2359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='block_timespan',
        ),
        migrations.AddField(
            model_name='customuser',
            name='permanent_block_interval',
            field=models.SmallIntegerField(blank=True, choices=[(3, 'six months'), (4, 'one year'), (5, 'three years'), (6, 'five years')], null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='permanent_block_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='permanent_block_timespan',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='temporary_block_interval',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'day'), (1, 'week'), (2, 'month')], null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='temporary_block_timespan',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='limitation',
            name='expiration_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='limitation',
            name='interval',
            field=models.SmallIntegerField(choices=[(0, 'day'), (1, 'week'), (2, 'month')], default=0, null=True),
        ),
    ]
