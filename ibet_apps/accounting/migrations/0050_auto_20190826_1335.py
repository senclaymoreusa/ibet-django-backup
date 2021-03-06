# Generated by Django 2.1.7 on 2019-08-26 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0049_auto_20190822_2236'),
    ]

    operations = [
        migrations.AddField(
            model_name='depositchannel',
            name='supplier',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='withdrawchannel',
            name='supplier',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='review_status',
            field=models.SmallIntegerField(choices=[(0, 'APPROVED'), (1, 'PENDING'), (2, 'REJECTED'), (3, 'SUCCESSFUL'), (4, 'FAILED'), (5, 'RESEND')], default=1, verbose_name='Review status'),
        ),
    ]
