# Generated by Django 2.1.7 on 2019-06-21 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0011_auto_20190619_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_choice',
            field=models.CharField(choices=[('U', 'Unicast')], default='U', max_length=1),
        ),
    ]
