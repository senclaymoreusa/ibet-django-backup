# Generated by Django 2.1.7 on 2019-10-25 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0059_transaction_qrcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depositchannel',
            name='market',
            field=models.SmallIntegerField(choices=[(0, 'ibet-VN'), (1, 'ibet-TH'), (2, 'ibet-CN')]),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='market',
            field=models.SmallIntegerField(choices=[(0, 'ibet-VN'), (1, 'ibet-TH'), (2, 'ibet-CN')]),
        ),
    ]
