# Generated by Django 2.1.1 on 2019-03-19 17:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_auto_20190319_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='referred_who',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
