# Generated by Django 2.1.7 on 2019-11-11 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0036_auto_20191108_1049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamebet',
            name='amount_wagered',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
