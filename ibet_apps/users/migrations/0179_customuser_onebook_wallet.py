# Generated by Django 2.1.7 on 2019-10-30 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0178_auto_20191029_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='onebook_wallet',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20, null=True, verbose_name='Onebook Wallet'),
        ),
    ]
