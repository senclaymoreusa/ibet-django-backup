# Generated by Django 2.1.7 on 2019-06-18 22:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0009_auto_20190617_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notifiers',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
