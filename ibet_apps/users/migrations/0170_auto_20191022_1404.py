# Generated by Django 2.1.7 on 2019-10-22 21:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0169_merge_20191021_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='address_verified',
            field=models.BooleanField(default=False, null=True,  blank=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='email_verified',
            field=models.BooleanField(default=False, null=True,  blank=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='id_verified',
            field=models.BooleanField(default=False, null=True,  blank=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone_verified',
            field=models.BooleanField(default=False, null=True,  blank=True),
        ),
    ]
