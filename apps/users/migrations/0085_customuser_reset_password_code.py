# Generated by Django 2.1.7 on 2019-05-13 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0084_merge_20190513_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='reset_password_code',
            field=models.CharField(blank=True, max_length=4),
        ),
    ]
