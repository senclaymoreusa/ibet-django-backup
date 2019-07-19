# Generated by Django 2.1.7 on 2019-06-14 19:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0096_auto_20190606_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkHistory',
            fields=[
                ('history_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='User Click Time')),
                ('user_ip', models.GenericIPAddressField(null=True, verbose_name='Action Ip')),
            ],
        ),
        migrations.CreateModel(
            name='ReferLink',
            fields=[
                ('refer_link_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('refer_link_url', models.URLField(unique=True)),
                ('refer_link_name', models.CharField(default='Default', max_length=50)),
                ('genarate_time', models.DateTimeField(auto_now_add=True, verbose_name='Created Time')),
            ],
        ),
        migrations.CreateModel(
            name='UserReferLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.ReferLink', verbose_name='Link')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.AddField(
            model_name='linkhistory',
            name='link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.ReferLink', verbose_name='Link'),
        ),
    ]