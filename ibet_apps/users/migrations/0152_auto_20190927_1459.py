# Generated by Django 2.1.7 on 2019-09-27 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0151_auto_20190927_1146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userreferlink',
            name='link',
        ),
        migrations.RemoveField(
            model_name='userreferlink',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserReferLink',
        ),
    ]
