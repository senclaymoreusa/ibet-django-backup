# Generated by Django 2.1.7 on 2019-09-11 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0137_auto_20190910_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='image_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
