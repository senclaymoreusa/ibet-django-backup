# Generated by Django 2.1.7 on 2019-05-14 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_depositchannel_deposit_channel'),
        ('users', '0082_merge_20190507_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='user_channel',
            field=models.ManyToManyField(blank=True, to='accounting.DepositChannel'),
        ),
    ]
