# Generated by Django 2.1.7 on 2019-07-12 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0024_auto_20190708_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='audit_date',
            field=models.DateTimeField(blank=True, verbose_name='Audit Date'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_method',
            field=models.CharField(choices=[('D', 'direct'), ('P', 'push'), ('S', 'sms'), ('E', 'email')], default='P', max_length=10),
        ),
    ]
