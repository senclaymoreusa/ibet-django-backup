# Generated by Django 2.1.15 on 2020-01-30 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0206_auto_20200129_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='ftd_time_amount',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Amount of FTD'),
        ),
    ]
