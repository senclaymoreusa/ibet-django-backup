# Generated by Django 2.1.7 on 2019-07-24 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_game_jackpot_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameattribute',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
