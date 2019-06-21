# Generated by Django 2.1.7 on 2019-06-21 19:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0025_auto_20190620_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.CharField(default=0, max_length=200, verbose_name='Transaction number'),
        ),
    ]
