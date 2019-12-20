# Generated by Django 2.1.7 on 2019-12-02 18:48

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0069_merge_20191115_1518'),
    ]

    operations = [
        migrations.RenameField(
            model_name='depositchannel',
            old_name='switch',
            new_name='status',
        ),
        migrations.RenameField(
            model_name='withdrawchannel',
            old_name='switch',
            new_name='status',
        ),
        migrations.AddField(
            model_name='depositchannel',
            name='blacklist',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='depositchannel',
            name='downtime_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='depositchannel',
            name='downtime_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='depositchannel',
            name='whitelist',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='withdrawchannel',
            name='blacklist',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='withdrawchannel',
            name='downtime_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='withdrawchannel',
            name='downtime_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='withdrawchannel',
            name='whitelist',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]