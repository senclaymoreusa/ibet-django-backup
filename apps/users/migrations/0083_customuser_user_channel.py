# Generated by Django 2.1.7 on 2019-05-14 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20190514_1237'),
        ('users', '0082_merge_20190507_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='user_channel',
            field=models.ManyToManyField(blank=True, through='accounting.DepositAccessManagement', to='accounting.DepositChannel'),
        ),
    ]
