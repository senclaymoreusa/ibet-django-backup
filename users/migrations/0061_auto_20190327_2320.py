# Generated by Django 2.1.1 on 2019-03-28 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0060_auto_20190327_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='activation',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
    ]
