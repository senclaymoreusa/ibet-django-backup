# Generated by Django 2.1.7 on 2019-12-05 00:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0193_customuser_ime_wallet'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='ime_wallet',
            new_name='imes_wallet',
        ),
    ]
