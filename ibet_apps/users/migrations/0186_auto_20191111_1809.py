# Generated by Django 2.1.7 on 2019-11-12 02:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0185_auto_20191107_1343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='address_verified',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='email_verified',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='id_verified',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='phone_verified',
        ),
    ]
