# Generated by Django 2.1.1 on 2019-03-29 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0063_merge_20190328_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='activation',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
    ]