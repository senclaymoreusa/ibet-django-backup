# Generated by Django 2.1.7 on 2019-03-29 23:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0064_auto_20190329_1516'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='activation',
            new_name='activation_code',
        ),
    ]