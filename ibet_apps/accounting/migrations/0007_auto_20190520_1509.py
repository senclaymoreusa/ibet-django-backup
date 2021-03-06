# Generated by Django 2.1.7 on 2019-05-20 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0006_auto_20190520_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'PHP'), (3, 'IDR')], default=0, verbose_name='Currency'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='order_id',
            field=models.CharField(default=0, max_length=100, verbose_name='Order id'),
        ),
    ]
