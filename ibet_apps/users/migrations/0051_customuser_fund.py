# Generated by Django 2.1.1 on 2019-03-22 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0050_config_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='fund',
            field=models.IntegerField(default=0),
        ),
    ]
