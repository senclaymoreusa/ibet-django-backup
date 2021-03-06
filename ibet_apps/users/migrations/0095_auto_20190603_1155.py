# Generated by Django 2.1.7 on 2019-06-03 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0094_merge_20190531_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created Time'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='modified_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Modified Time'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='time_of_registration',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Time of Registration'),
        ),
        migrations.AlterField(
            model_name='useraction',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created Time'),
        ),
    ]
