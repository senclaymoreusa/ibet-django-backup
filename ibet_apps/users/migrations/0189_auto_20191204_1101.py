# Generated by Django 2.1.7 on 2019-12-04 19:01

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0188_merge_20191113_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraction',
            name='ip_location',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, null=True),
        ),
        migrations.AddField(
            model_name='useraction',
            name='other_info',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, null=True),
        ),
        migrations.AddField(
            model_name='useraction',
            name='real_ip',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='useraction',
            name='result',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
