# Generated by Django 2.1.7 on 2019-10-31 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0032_auto_20191031_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameprovider',
            name='notes',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='gameprovider',
            name='market',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
