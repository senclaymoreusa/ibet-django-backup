# Generated by Django 2.1.15 on 2020-01-16 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0068_gamethirdpartyaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamebet',
            name='result',
            field=models.SmallIntegerField(choices=[(0, 'Open'), (1, 'Close')], default=0),
        ),
    ]
