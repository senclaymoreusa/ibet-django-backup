# Generated by Django 2.1.7 on 2019-10-16 23:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0015_auto_20191016_1607'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fgsession',
            old_name='user_name',
            new_name='user',
        ),
    ]
