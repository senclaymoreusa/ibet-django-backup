# Generated by Django 2.1.7 on 2019-11-05 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0183_auto_20191104_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='member_status',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Normal'), (1, 'Suspicious'), (2, 'Restricted'), (3, 'Closed'), (4, 'Blacklisted')], default=0, null=True),
        ),
    ]
