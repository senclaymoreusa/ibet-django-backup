# Generated by Django 2.1.1 on 2019-03-27 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0058_auto_20190327_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='activation',
            field=models.CharField(default='', max_length=300),
        ),
    ]