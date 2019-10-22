# Generated by Django 2.1.7 on 2019-09-27 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0149_auto_20190927_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referlink',
            name='refer_link_name',
            field=models.CharField(default='default', max_length=50),
        ),
        migrations.AlterField(
            model_name='referlink',
            name='refer_link_url',
            field=models.URLField(blank=True, null=True, unique=True),
        ),
    ]