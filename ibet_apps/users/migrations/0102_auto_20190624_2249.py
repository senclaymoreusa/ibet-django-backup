# Generated by Django 2.1.7 on 2019-06-25 05:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0101_auto_20190623_2154'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LimitationTable',
            new_name='Limitation',
        ),
    ]