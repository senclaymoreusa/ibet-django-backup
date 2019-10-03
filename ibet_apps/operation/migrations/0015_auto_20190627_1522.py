# Generated by Django 2.1.7 on 2019-06-27 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0014_auto_20190626_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_method',
            field=models.CharField(choices=[('D', 'direct'), ('P', 'push'), ('S', 'sms'), ('E', 'email')], default='P', max_length=3),
        ),
    ]
