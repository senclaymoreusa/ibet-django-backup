# Generated by Django 2.1.7 on 2019-09-27 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0147_merge_20190923_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractivity',
            name='activity_type',
            field=models.SmallIntegerField(choices=[(0, 'System'), (1, 'Remark'), (2, 'Message'), (3, 'Note')], default=0),
        ),
    ]
