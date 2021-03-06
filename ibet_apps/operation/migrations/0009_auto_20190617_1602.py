# Generated by Django 2.1.7 on 2019-06-17 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0008_auto_20190614_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notification_choice',
            field=models.CharField(choices=[('U', 'Unicast'), ('B', 'Broadcast')], default='U', max_length=1),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_method',
            field=models.CharField(choices=[('P', 'push'), ('S', 'sms'), ('E', 'email')], default='P', max_length=3),
        ),
    ]
