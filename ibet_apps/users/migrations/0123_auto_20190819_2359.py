# Generated by Django 2.1.7 on 2019-08-20 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0122_merge_20190819_0901'),
    ]

    operations = [
        migrations.CreateModel(
            name='GBSportWallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Method', models.CharField(max_length=30)),
                ('Success', models.CharField(choices=[('1', '1'), ('0', '0')], max_length=1)),
                ('TransType', models.CharField(choices=[('Bet', 'Bet'), ('Discard', 'Discard'), ('Settle', 'Settle'), ('Balance', 'Balance')], max_length=20)),
                ('ThirdPartyCode', models.CharField(max_length=30)),
                ('BetTotalCnt', models.CharField(max_length=30)),
                ('BetTotalAmt', models.CharField(max_length=30)),
                ('BetID', models.CharField(max_length=20)),
                ('SettleID', models.CharField(max_length=20)),
                ('BetGrpNO', models.CharField(max_length=50)),
                ('TPCode', models.CharField(max_length=30)),
                ('GBSN', models.CharField(max_length=30)),
                ('MemberID', models.CharField(max_length=30)),
                ('CurCode', models.CharField(max_length=30)),
                ('BetDT', models.CharField(max_length=100)),
                ('BetType', models.CharField(max_length=20)),
                ('BetTypeParam1', models.CharField(max_length=20)),
                ('BetTypeParam2', models.CharField(max_length=20)),
                ('Wintype', models.CharField(max_length=20)),
                ('HxMGUID', models.CharField(max_length=20)),
                ('InitBetAmt', models.CharField(max_length=30)),
                ('RealBetAmt', models.CharField(max_length=30)),
                ('HoldingAmt', models.CharField(max_length=30)),
                ('InitBetRate', models.CharField(max_length=30)),
                ('RealBetRate', models.CharField(max_length=20)),
                ('PreWinAmt', models.CharField(max_length=30)),
                ('BetResult', models.CharField(max_length=30)),
                ('WLAmt', models.CharField(max_length=30)),
                ('RefundBetAmt', models.CharField(max_length=30)),
                ('TicketBetAmt', models.CharField(max_length=30)),
                ('TicketResult', models.CharField(max_length=30)),
                ('TicketWLAmt', models.CharField(max_length=30)),
                ('SettleDT', models.CharField(max_length=30)),
            ],
        ),
        migrations.RemoveField(
            model_name='betkenoballs',
            name='DetailID',
        ),
        migrations.RemoveField(
            model_name='betkenolist',
            name='BetID',
        ),
        migrations.RemoveField(
            model_name='settlekenoballs',
            name='DetailID',
        ),
        migrations.RemoveField(
            model_name='settlekenolist',
            name='SettleOID',
        ),
        migrations.DeleteModel(
            name='BetKenoBalls',
        ),
        migrations.DeleteModel(
            name='BetKenoList',
        ),
        migrations.DeleteModel(
            name='GBSportWalletBet',
        ),
        migrations.DeleteModel(
            name='GBSportWalletSettle',
        ),
        migrations.DeleteModel(
            name='SettleKenoBalls',
        ),
        migrations.DeleteModel(
            name='SettleKenoList',
        ),
    ]
