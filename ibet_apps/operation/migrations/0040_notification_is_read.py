# Generated by Django 2.1.7 on 2019-08-14 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0039_auto_20190814_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
