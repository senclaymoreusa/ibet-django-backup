# Generated by Django 2.1.7 on 2020-01-29 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0205_customuser_gpi_wallet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='ag_wallet',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='ea_wallet',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='gpi_wallet',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='ky_wallet',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='onebook_wallet',
        ),
    ]
