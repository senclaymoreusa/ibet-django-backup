# Generated by Django 2.1.7 on 2019-10-17 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0009_eaticket'),
    ]

    operations = [
        migrations.CreateModel(
            name='GDCasino',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('method', models.CharField(max_length=100)),
                ('currency', models.CharField(max_length=100)),
                ('merchant_id', models.CharField(max_length=100)),
                ('message_id', models.CharField(max_length=100)),
            ],
        ),
    ]
