# Generated by Django 2.1.7 on 2019-11-09 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0037_remove_gamebet_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamebet',
            name='transaction_id',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
