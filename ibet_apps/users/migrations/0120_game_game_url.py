# Generated by Django 2.1.7 on 2019-08-14 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0119_auto_20190807_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_url',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
