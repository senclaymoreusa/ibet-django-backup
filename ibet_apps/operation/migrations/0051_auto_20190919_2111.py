# Generated by Django 2.1.7 on 2019-09-20 04:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0008_auto_20190919_1628'),
        ('operation', '0050_auto_20190919_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='CampaignToGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='group',
        ),
        migrations.AddField(
            model_name='campaigntogroup',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='operation.Campaign'),
        ),
        migrations.AddField(
            model_name='campaigntogroup',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.UserGroup'),
        ),
    ]