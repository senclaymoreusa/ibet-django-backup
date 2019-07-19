# Generated by Django 2.1.7 on 2019-06-11 21:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operation', '0003_pushnoticemessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(default='', max_length=100)),
                ('notification_type', models.IntegerField()),
                ('publish_time', models.DateField(verbose_name='Publish Time')),
                ('create_on', models.DateTimeField(verbose_name='Create Time')),
                ('publish_on', models.DateTimeField(verbose_name='Publish Time')),
            ],
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(default='', max_length=30)),
                ('act_on', models.DateTimeField(verbose_name='Action Time')),
                ('actor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('notification_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operation.Notification')),
            ],
        ),
        migrations.CreateModel(
            name='NotificationUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operation.Notification')),
                ('notifier_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='PushNoticeMessage',
        ),
    ]