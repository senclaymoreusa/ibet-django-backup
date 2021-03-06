# Generated by Django 2.1.7 on 2019-11-01 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0013_auto_20191028_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonus',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR'), (4, 'HKD'), (5, 'AUD'), (6, 'MYR'), (7, 'VND'), (8, 'MMK'), (9, 'XBT'), (10, 'EUR'), (11, 'NOK'), (12, 'GBP'), (20, 'UUD')], default=0, verbose_name='Bonus Currency'),
        ),
    ]
