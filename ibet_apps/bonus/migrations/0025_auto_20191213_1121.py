# Generated by Django 2.1.7 on 2019-12-13 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0024_auto_20191205_1031'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonus',
            name='max_amount',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bonus',
            name='max_user_amount',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bonus',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bonus.Bonus'),
        ),
    ]