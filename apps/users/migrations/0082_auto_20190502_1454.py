# Generated by Django 2.1.7 on 2019-05-02 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0081_merge_20190502_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraction',
            name='dollow_amount',
            field=models.FloatField(blank=True, null=True),
        ),
    ]