# Generated by Django 2.1.7 on 2019-11-07 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0064_auto_20191104_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='depositaccessmanagement',
            name='deposit_favorite_method',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]