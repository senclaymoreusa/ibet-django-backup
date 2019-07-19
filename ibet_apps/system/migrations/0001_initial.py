# Generated by Django 2.1.7 on 2019-07-01 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PermissionGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_code', models.CharField(max_length=50, verbose_name='Permission Code')),
            ],
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='Description')),
                ('groupType', models.SmallIntegerField(blank=True, choices=[(0, 'Permission'), (1, 'other')], null=True, verbose_name='Group Type')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Created Time')),
            ],
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_code', models.CharField(max_length=50, verbose_name='Permission Code')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Custom User')),
            ],
        ),
        migrations.CreateModel(
            name='UserToUserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.UserGroup', verbose_name='User Group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Custom User')),
            ],
        ),
        migrations.AddField(
            model_name='permissiongroup',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.UserGroup', verbose_name='User Group'),
        ),
    ]