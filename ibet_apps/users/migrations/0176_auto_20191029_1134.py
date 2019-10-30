# Generated by Django 2.1.7 on 2019-10-29 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0175_auto_20191029_1131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='currency',
        ),

        migrations.AddField(
            model_name='customuser',
            name='currency',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR'), (4, 'HKD'), (5, 'AUD'), (6, 'MYR'), (7, 'VND'), (8, 'MMK'), (9, 'XBT'), (10, 'EUR'), (11, 'NOK'), (12, 'GBP')], default=0),
        ),
    ]