# Generated by Django 2.1.7 on 2019-06-14 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0021_merge_20190614_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depositchannel',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR')], default=0, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR')], default=0, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'SUCCESS'), (1, 'FAILED'), (2, 'CREATED'), (3, 'PENDING'), (4, 'APPROVED'), (5, 'REJECTED'), (6, 'COMPLETED')], default=2, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='currency',
            field=models.SmallIntegerField(choices=[(0, 'CNY'), (1, 'USD'), (2, 'THB'), (3, 'IDR')], default=0, verbose_name='Currency'),
        ),
    ]
