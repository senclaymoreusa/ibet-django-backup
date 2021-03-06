# Generated by Django 2.1.7 on 2019-08-07 22:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bonus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBonus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(verbose_name='Start Time')),
                ('is_successful', models.BooleanField(default=False)),
                ('bonus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bonus.Bonus', verbose_name='Bonus')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
