# Generated by Django 2.1.7 on 2019-12-07 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0058_auto_20191205_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameprovider',
            name='is_transfer_wallet',
            field=models.BooleanField(default=True),
        ),
    ]
