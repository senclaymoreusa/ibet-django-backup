# Generated by Django 2.1.7 on 2019-05-31 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0011_auto_20190529_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='product',
            field=models.SmallIntegerField(choices=[(0, 'Sports'), (1, 'Games'), (2, 'Live Casino'), (3, 'Financial'), (4, 'General')], default=4, verbose_name='Product'),
        ),
    ]
