# Generated by Django 2.1.7 on 2019-12-09 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0060_auto_20191205_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamebet',
            name='user_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
