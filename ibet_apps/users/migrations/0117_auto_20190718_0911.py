# Generated by Django 2.1.7 on 2019-07-18 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0116_aggamemodels'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='main_wallet',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Main Wallet'),
        ),
    ]
