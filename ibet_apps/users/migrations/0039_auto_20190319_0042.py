# Generated by Django 2.1.1 on 2019-03-19 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_auto_20190319_0009'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referraluser',
            name='user',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='referred_who',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.DeleteModel(
            name='ReferralUser',
        ),
    ]
