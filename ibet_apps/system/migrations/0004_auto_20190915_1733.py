# Generated by Django 2.1.7 on 2019-09-16 00:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('system', '0003_auto_20190731_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='time_used',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='groupType',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Permission'), (2, 'message'), (1, 'other')], null=True, verbose_name='Group Type'),
        ),
    ]