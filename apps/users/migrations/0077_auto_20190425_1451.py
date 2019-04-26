# Generated by Django 2.1.7 on 2019-04-25 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0076_auto_20190418_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='currency',
            field=models.CharField(blank=True, choices=[('usd', 'USD'), ('eur', 'EUR'), ('jpy', 'JPY'), ('cny', 'CNY'), ('hkd', 'HKD'), ('aud', 'AUD')], max_length=30),
        ),
    ]