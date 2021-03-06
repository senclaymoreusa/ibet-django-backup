# Generated by Django 2.1.7 on 2019-04-04 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0066_merge_20190402_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='contact_option',
            field=models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('oms', 'OMS'), ('push_notification', 'Push Notification')], default='email', max_length=6),
        ),
        migrations.AddField(
            model_name='customuser',
            name='currency',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='customuser',
            name='deposit_limit',
            field=models.FloatField(default=100),
        ),
        migrations.AddField(
            model_name='customuser',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='male', max_length=6),
        ),
        migrations.AddField(
            model_name='customuser',
            name='odds_display',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='over_eighteen',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='preferred_team',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='customuser',
            name='promo_code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='title',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)", max_length=200),
        ),
    ]
