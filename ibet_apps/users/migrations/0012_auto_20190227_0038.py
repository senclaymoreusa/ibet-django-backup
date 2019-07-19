# Generated by Django 2.1.7 on 2019-02-27 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_customuser_block'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name_fr',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_zh',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='description_fr',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='description_zh',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='name_fr',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='name_zh',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]