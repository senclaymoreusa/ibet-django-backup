# Generated by Django 2.1.7 on 2019-07-16 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_auto_20190715_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='jackpot_size',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]