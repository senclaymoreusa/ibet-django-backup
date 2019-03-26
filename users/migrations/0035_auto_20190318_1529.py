# Generated by Django 2.1.1 on 2019-03-18 22:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_auto_20190318_1427'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='referred_who',
        ),
        migrations.AddField(
            model_name='customuser',
            name='referred_who',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]