# Generated by Django 2.1.7 on 2019-10-21 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0160_merge_20191014_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='currency',
            field=models.CharField(blank=True, choices=[('USD', 'USD'), ('EUR', 'EUR'), ('JPY', 'JPY'), ('CNY', 'CNY'), ('HKD', 'HKD'), ('AUD', 'AUD'), ('THB', 'THB'), ('MYR', 'MYR'), ('VND', 'VND'), ('MMK', 'MMK'), ('XBT', 'XBT'), ('TTC', 'TTC')], default='USD', max_length=30),
        ),
    ]
