# Generated by Django 2.1.7 on 2019-08-29 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0128_auto_20190828_1633'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AGGamemodels',
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='Round',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='agentCode',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='amount',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='betTime',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='billNo',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='currency',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='deviceType',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='finish',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='gameCode',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='gameId',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='gameResult',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='gametype',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='netAmount',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='platformType',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='playname',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='playtype',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='remark',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='roundId',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='sessionToken',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='settletime',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='tableCode',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='ticketStatus',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='time',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='transactionCode',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='transactionID',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='transactionType',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='validBetAmount',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='gamerequestsmodel',
            name='value',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]