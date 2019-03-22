# Generated by Django 2.1.1 on 2019-03-20 02:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0041_auto_20190319_1401'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referred', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referred', to=settings.AUTH_USER_MODEL)),
                ('referrer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='hop',
            unique_together={('referrer', 'referred')},
        ),
    ]
