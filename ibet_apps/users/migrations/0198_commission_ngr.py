# Generated by Django 2.1.7 on 2019-12-18 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0197_merge_20191212_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='commission',
            name='ngr',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
    ]
