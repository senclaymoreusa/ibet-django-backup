# Generated by Django 2.1.7 on 2019-12-10 00:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0062_merge_20191209_1607'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gamebet',
            old_name='username',
            new_name='user',
        ),
    ]
