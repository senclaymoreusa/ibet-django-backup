# Generated by Django 2.1.7 on 2019-09-26 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0141_auto_20190926_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='txn_reverse_id',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]