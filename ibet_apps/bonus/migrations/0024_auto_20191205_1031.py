# Generated by Django 2.1.7 on 2019-12-05 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0023_remove_bonus_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonus',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
