# Generated by Django 2.1.7 on 2019-07-23 23:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0028_awstopic_creator'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NoticeMessage',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='create_date',
            new_name='create_on',
        ),
        migrations.AlterField(
            model_name='notification',
            name='creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]