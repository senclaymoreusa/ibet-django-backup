# Generated by Django 2.1.1 on 2019-03-19 04:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_auto_20190318_1529'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='referred_who',
        ),
        migrations.AddField(
            model_name='customuser',
            name='referred_who',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
