# Generated by Django 2.1.1 on 2019-02-18 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_remove_customuser_zipcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='zipcode',
            field=models.CharField(default='92612', max_length=100),
            preserve_default=False,
        ),
    ]
