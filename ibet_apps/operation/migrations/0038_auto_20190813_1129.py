# Generated by Django 2.1.7 on 2019-08-13 18:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operation', '0037_auto_20190812_1709'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationlog',
            name='action',
        ),
        migrations.AddField(
            model_name='notificationlog',
            name='actor_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notificationlog',
            name='group_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='operation.AWSTopic'),
        ),
    ]