# Generated by Django 2.1.7 on 2019-09-11 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0046_notificationtousers_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL),
        ),
    ]
