# Generated by Django 2.1.7 on 2019-05-21 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0008_auto_20190521_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Amount'),
        ),
    ]
