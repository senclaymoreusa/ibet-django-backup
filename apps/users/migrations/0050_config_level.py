# Generated by Django 2.1.1 on 2019-03-20 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0049_auto_20190319_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='level',
            field=models.IntegerField(default=2),
        ),
    ]