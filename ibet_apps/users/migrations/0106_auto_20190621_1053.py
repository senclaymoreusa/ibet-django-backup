# Generated by Django 2.1.7 on 2019-06-21 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0105_auto_20190621_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(max_length=25),
        ),
    ]
