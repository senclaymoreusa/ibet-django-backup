# Generated by Django 2.1.7 on 2019-12-03 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0056_merge_20191127_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamebet',
            name='market',
            field=models.SmallIntegerField(choices=[(0, 'ibet-VN'), (1, 'ibet-TH'), (2, 'ibet-CN'), (3, 'letou-VN'), (4, 'letou-TH'), (5, 'letou-CN')]),
        ),
    ]
