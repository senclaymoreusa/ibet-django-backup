# Generated by Django 2.1.7 on 2019-11-15 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0044_auto_20191113_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='game_image'),
        ),
    ]
