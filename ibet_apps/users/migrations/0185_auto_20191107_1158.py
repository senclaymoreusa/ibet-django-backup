# Generated by Django 2.1.7 on 2019-11-07 19:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0184_merge_20191106_1748'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='managed_by',
        ),
        migrations.AddField(
            model_name='customuser',
            name='affiliate_managed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='AffiliateManager', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customuser',
            name='vip_managed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='VIPManager', to=settings.AUTH_USER_MODEL),
        ),
    ]
