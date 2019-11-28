# Generated by Django 2.1.7 on 2019-10-25 01:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0171_merge_20191023_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='referred_by_channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.ReferChannel'),
        ),
    ]