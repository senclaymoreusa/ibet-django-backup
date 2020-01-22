# Generated by Django 2.1.7 on 2020-01-09 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0028_auto_20200107_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbonusevent',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'ISSUED'), (1, 'CLAIMED'), (2, 'START'), (3, 'ACTIVE'), (4, 'COMPLETED'), (5, 'EXPIRED'), (6, 'CANCELLED'), (7, 'PENDING'), (8, 'RELEASED')], default=0, verbose_name='User Bonus Event Type'),
        ),
    ]