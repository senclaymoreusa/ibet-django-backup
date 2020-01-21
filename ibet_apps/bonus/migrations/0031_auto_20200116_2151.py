# Generated by Django 2.1.7 on 2020-01-17 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0030_remove_bonus_max_user_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonus',
            name='delivery',
            field=models.SmallIntegerField(choices=[(0, 'Push'), (1, 'Site activation')], default=0),
        ),
    ]
