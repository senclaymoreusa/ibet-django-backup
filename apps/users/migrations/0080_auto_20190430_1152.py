# Generated by Django 2.1.7 on 2019-04-30 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0079_merge_20190426_1201'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userwithtag',
            options={'verbose_name': 'Tag', 'verbose_name_plural': 'Assign tag to user'},
        ),
    ]
