# Generated by Django 2.1.7 on 2019-04-05 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0068_auto_20190404_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=6),
        ),
    ]
