# Generated by Django 2.1.7 on 2019-06-10 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0096_merge_20190610_1559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='commission_last_month',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='commission_this_month',
        ),
        migrations.AddField(
            model_name='customuser',
            name='commision_percentage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Commision Percentage'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='commision_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_application_time',
            field=models.DateTimeField(default=None, null=True, verbose_name='Application Time'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_to_agent',
            field=models.DateTimeField(default=None, null=True, verbose_name='Time of Becoming Agent'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='agent_level',
            field=models.CharField(choices=[('Premium', 'Premium'), ('Invalid', 'Invalid'), ('Normal', 'Normal'), ('Negative', 'Negative')], default='Normal', max_length=255, verbose_name='Agent Level'),
        ),
    ]
