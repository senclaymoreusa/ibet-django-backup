# Generated by Django 2.1.7 on 2019-10-18 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0013_auto_20191018_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gdgetuserbalance',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
