# Generated by Django 2.1.7 on 2019-09-24 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0055_transaction_release_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='month',
            field=models.DateField(blank=True, null=True),
        ),
    ]