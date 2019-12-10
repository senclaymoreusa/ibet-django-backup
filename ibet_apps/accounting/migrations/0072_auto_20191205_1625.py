# Generated by Django 2.1.7 on 2019-12-06 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0071_auto_20191205_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='product',
            field=models.SmallIntegerField(choices=[(0, 'Sports'), (1, 'Games'), (2, 'Live Casino'), (3, 'Table Games'), (4, 'General')], default=4, verbose_name='Product'),
        ),
    ]
