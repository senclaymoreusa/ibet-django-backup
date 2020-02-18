# Generated by Django 2.1.15 on 2020-01-31 23:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0208_customuser_member_changed_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='member_changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='MemberChange', to=settings.AUTH_USER_MODEL),
        ),
    ]
