# Generated by Django 2.1.7 on 2019-12-04 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0190_remove_useraction_real_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraction',
            name='browser',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Browser'),
        ),
    ]