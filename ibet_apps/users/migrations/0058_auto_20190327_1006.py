# Generated by Django 2.1.1 on 2019-03-27 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0057_customuser_is_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='is_active',
            new_name='active',
        ),
    ]
