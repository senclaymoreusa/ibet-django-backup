# Generated by Django 2.1.7 on 2019-11-19 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0042_merge_20191118_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamebet',
            name='bet_type',
            field=models.CharField(blank=True, choices=[('SPREAD', 'Spread'), ('LINE', 'Moneyline'), ('OU', 'Total O/U'), ('TIP', 'Tip'), ('Single', 'Single'), ('Parlay', 'Parlay')], max_length=6, null=True),
        ),
    ]
