# Generated by Django 2.1.1 on 2019-03-20 05:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0046_customuser_referred_who'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='referral',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='referral',
            name='referred',
        ),
        migrations.RemoveField(
            model_name='referral',
            name='referrer',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='referred_who',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='referred_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referees', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Referral',
        ),
    ]
