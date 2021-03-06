# Generated by Django 2.1.7 on 2019-04-12 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NoticeMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(verbose_name='Start Time')),
                ('end_time', models.DateTimeField(verbose_name='End Time')),
                ('message', models.CharField(default='', max_length=200)),
                ('message_zh', models.CharField(default='', max_length=200)),
                ('message_fr', models.CharField(default='', max_length=200)),
            ],
        ),
    ]
