# Generated by Django 2.1.7 on 2019-02-26 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_customuser_zipcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='block',
            field=models.BooleanField(default=False),
        ),
    ]
