# Generated by Django 2.1.7 on 2019-06-21 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0104_customuser_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='state',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]