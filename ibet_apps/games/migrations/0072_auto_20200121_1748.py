# Generated by Django 2.1.7 on 2020-01-22 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0071_merge_20200117_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamebet',
            name='outcome',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Win'), (1, 'Lose'), (2, 'Tie/Push'), (3, 'Void')], null=True),
        ),
    ]
