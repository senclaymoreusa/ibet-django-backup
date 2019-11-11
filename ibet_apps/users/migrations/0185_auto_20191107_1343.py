# Generated by Django 2.1.7 on 2019-11-07 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0184_auto_20191105_1342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='user_deposit_channel',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='user_withdraw_channel',
        ),
        migrations.AddField(
            model_name='customuser',
            name='favorite_payment_method',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
