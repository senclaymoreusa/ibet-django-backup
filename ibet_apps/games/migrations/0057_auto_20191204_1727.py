# Generated by Django 2.1.7 on 2019-12-05 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0056_merge_20191127_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='is_free',
            field=models.NullBooleanField(default=None),
        ),
    ]
