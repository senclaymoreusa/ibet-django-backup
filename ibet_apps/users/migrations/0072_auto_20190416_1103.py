# Generated by Django 2.1.7 on 2019-04-16 18:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0071_auto_20190415_1155'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='userTag',
            new_name='user_tag',
        ),
    ]
