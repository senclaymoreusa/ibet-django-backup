# Generated by Django 2.1.7 on 2019-08-07 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0119_merge_20190806_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='department',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]