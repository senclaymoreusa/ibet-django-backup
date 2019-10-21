# Generated by Django 2.1.7 on 2019-09-17 19:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0139_merge_20190916_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commission_set', models.CharField(choices=[('System', 'System'), ('Personal', 'Personal')], default='System', max_length=50, verbose_name='Commission_set')),
                ('commision_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Commision Percentage')),
                ('downline_commision_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Downline Commision Percentage')),
                ('commission_level', models.IntegerField(default=1)),
                ('active_downline_needed', models.IntegerField(default=6)),
                ('monthly_downline_ftd_needed', models.IntegerField(default=6)),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='commision_percentage',
        ),
        migrations.AddField(
            model_name='customuser',
            name='affiliate_level',
            field=models.CharField(choices=[('Normal', 'Normal'), ('VIP', 'VIP')], default='Normal', max_length=50, verbose_name='Affiliate_level'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='affiliate_status',
            field=models.CharField(choices=[('Enabled', 'Enabled'), ('Disabled', 'Disabled')], default='Enabled', max_length=50, verbose_name='Affiliate_status'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='managed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manage', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customuser',
            name='transerfer_between_levels',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='agent_level',
            field=models.CharField(choices=[('Premium', 'Premium'), ('Invalid', 'Invalid'), ('Normal', 'Normal'), ('Negative', 'Negative')], max_length=50, null=True, verbose_name='Agent Level'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='agent_status',
            field=models.CharField(choices=[('Enabled', 'Enabled'), ('Disabled', 'Disabled')], default='Enabled', max_length=50, verbose_name='Agent Status'),
        ),
    ]
