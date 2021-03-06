# Generated by Django 2.1.7 on 2019-05-16 06:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0085_auto_20190514_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='created_time',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created Time'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='ftd_time',
            field=models.DateTimeField(default=None, null=True, verbose_name='Time of FTD'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='id_location',
            field=models.CharField(default='', max_length=300, verbose_name='Location shown on the ID'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_betting_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last Betting Time'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_login_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last Login Time'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='main_wallet',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Main Wallet'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='member_status',
            field=models.SmallIntegerField(blank=True, choices=[('0', 'Active'), ('1', 'Inactive'), ('2', 'Blocked')], null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='modified_time',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created Time'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='other_game_wallet',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Other Game Wallet'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='product_attribute',
            field=models.CharField(blank=True, default='', max_length=300, verbose_name='Product Attribute'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='time_of_registration',
            field=models.DateTimeField(default=None, null=True, verbose_name='Time of Registration'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_attribute',
            field=models.SmallIntegerField(choices=[('0', 'Direct User'), ('1', 'User from Promo'), ('2', 'Advertisements')], default='0', verbose_name='User Attribute'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='verfication_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Time of Verification'),
        ),
    ]
