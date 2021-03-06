# Generated by Django 2.1.7 on 2019-06-14 21:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operation', '0006_auto_20190614_0927'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notification_method',
            field=models.CharField(choices=[('U', 'Unicast'), ('B', 'Broadcast')], default='U', max_length=1),
        ),
        migrations.AddField(
            model_name='notification',
            name='notifiers',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.IntegerField(choices=[(1, 'ALERT')], default=1),
        ),
        migrations.AlterField(
            model_name='notificationlog',
            name='action',
            field=models.CharField(choices=[('C', 'CREATE'), ('U', 'UPDATE'), ('D', 'DELETE')], max_length=1),
        ),
    ]
