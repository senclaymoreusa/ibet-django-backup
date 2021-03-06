# Generated by Django 2.1.7 on 2019-05-24 23:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0090_auto_20190522_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonus',
            name='categories',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='bonus',
            name='countries',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='bonus',
            name='description',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='bonus',
            name='requirement_ids',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='bonusrequirement',
            name='categories',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='activation_code',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='currency',
            field=models.CharField(blank=True, choices=[('USD', 'USD'), ('EUR', 'EUR'), ('JPY', 'JPY'), ('CNY', 'CNY'), ('HKD', 'HKD'), ('AUD', 'AUD')], default='USD', max_length=30),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='id_location',
            field=models.CharField(default='', max_length=255, verbose_name='Location shown on the ID'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='product_attribute',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Product Attribute'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_username', message='Username must be alphanumeric or contain numbers', regex='^[a-zA-Z0-9.+-]*$')]),
        ),
        migrations.AlterField(
            model_name='useraction',
            name='refer_url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Refer URL'),
        ),
    ]
