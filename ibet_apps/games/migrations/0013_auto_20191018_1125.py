# Generated by Django 2.1.7 on 2019-10-18 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0012_auto_20191017_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gdgetuserbalance',
            name='id',
            field=models.CharField(editable=False, max_length=200, primary_key=True, serialize=False),
        ),
    ]
