# Generated by Django 2.1.1 on 2019-03-14 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_customuser_referral_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='referral_code',
            new_name='referral_link',
        ),
    ]