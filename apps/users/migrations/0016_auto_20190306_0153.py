# Generated by Django 2.1.7 on 2019-03-06 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20190306_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='street_address_2',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]