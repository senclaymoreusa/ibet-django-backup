# Generated by Django 2.1.7 on 2019-12-05 19:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0058_auto_20191205_1053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mgtoken',
            name='user',
        ),
        migrations.DeleteModel(
            name='MGToken',
        ),
    ]
