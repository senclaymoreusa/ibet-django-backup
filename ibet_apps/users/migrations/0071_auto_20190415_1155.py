# Generated by Django 2.1.7 on 2019-04-15 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0070_auto_20190415_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='userTag',
            field=models.ManyToManyField(blank=True, to='users.UserTag'),
        ),
    ]
