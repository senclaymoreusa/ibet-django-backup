# Generated by Django 2.1.7 on 2019-10-14 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0163_auto_20191013_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='referral_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='referlink',
            name='refer_link_code',
            field=models.CharField(max_length=100),
        ),
    ]
