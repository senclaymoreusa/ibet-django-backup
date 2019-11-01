# Generated by Django 2.1.7 on 2019-11-01 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0033_auto_20191031_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamebet',
            name='outcome',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Win'), (1, 'Lose'), (2, 'Tie/Push'), (3, 'Void'), (4, 'Running'), (5, 'Draw'), (6, 'Half lose')], null=True),
        ),
    ]
