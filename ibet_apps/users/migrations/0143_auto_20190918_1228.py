# Generated by Django 2.1.7 on 2019-09-18 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0142_auto_20190918_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='affiliate_status',
            field=models.CharField(blank=True, choices=[('Active', 'Active'), ('VIP', 'VIP'), ('Negative', 'Negative'), ('Deactivated', 'Deactivated')], max_length=50, null=True, verbose_name='Affiliate_status'),
        ),
    ]
