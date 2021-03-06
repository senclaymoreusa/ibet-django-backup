# Generated by Django 2.1.7 on 2019-12-05 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0070_merge_20191203_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depositchannel',
            name='market',
            field=models.SmallIntegerField(choices=[(0, 'ibet-VN'), (1, 'ibet-TH'), (2, 'ibet-CN'), (10, 'letou-VN'), (11, 'letou-TH'), (12, 'letou-CN')]),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='market',
            field=models.SmallIntegerField(choices=[(0, 'ibet-VN'), (1, 'ibet-TH'), (2, 'ibet-CN'), (10, 'letou-VN'), (11, 'letou-TH'), (12, 'letou-CN')]),
        ),
    ]
