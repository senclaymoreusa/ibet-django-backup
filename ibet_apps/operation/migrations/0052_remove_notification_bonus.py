# Generated by Django 2.1.7 on 2019-10-03 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0051_auto_20190919_2111'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='bonus',
        ),
    ]
