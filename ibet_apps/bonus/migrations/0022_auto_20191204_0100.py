# Generated by Django 2.1.7 on 2019-12-04 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0021_auto_20191203_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonus',
            name='description',
            field=models.TextField(null=True),
        ),
    ]