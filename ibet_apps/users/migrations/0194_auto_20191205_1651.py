# Generated by Django 2.1.7 on 2019-12-06 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0193_auto_20191205_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userwallet',
            name='wallet_amount',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Wallet'),
        ),
    ]
