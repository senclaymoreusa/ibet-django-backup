# Generated by Django 2.1.7 on 2019-07-25 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_auto_20190723_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='provider',
            field=models.SmallIntegerField(choices=[(0, 'Netent'), (1, "Play'n Go"), (2, 'Big Time Gaming'), (3, 'Microgaming'), (4, 'Quickspin'), (5, 'Progmatic Play'), (6, 'Blueprint'), (7, 'Novomatic'), (8, 'IGT'), (9, 'Elk Studio'), (10, 'Genesis'), (11, 'High5'), (12, 'Iron Dog'), (13, 'Just For The Win'), (14, 'Kalamba'), (15, 'Leander'), (16, 'Lightning Box'), (17, 'Nextgen'), (18, 'Red7'), (19, 'Red Tiger Gaming'), (20, 'Scientific Games'), (21, 'Thunderkick'), (22, 'Yggdrasil')], default=0),
        ),
    ]