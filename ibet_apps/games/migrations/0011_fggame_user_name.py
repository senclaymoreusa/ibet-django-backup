# Generated by Django 2.1.7 on 2019-10-15 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0010_fggame'),
    ]

    operations = [
        migrations.AddField(
            model_name='fggame',
            name='user_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
