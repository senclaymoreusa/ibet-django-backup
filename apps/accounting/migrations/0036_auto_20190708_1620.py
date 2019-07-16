# Generated by Django 2.1.7 on 2019-07-08 23:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0035_auto_20190708_1552'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='channel',
        ),
        migrations.AddField(
            model_name='depositchannel',
            name='transaction_fee',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, verbose_name='Transaction Fee'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='deposit_channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.DepositChannel'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='withdraw_channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.WithdrawChannel'),
        ),
        migrations.AlterField(
            model_name='depositchannel',
            name='bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Bank'),
        ),
        migrations.AlterField(
            model_name='withdrawchannel',
            name='bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Bank'),
        ),
    ]
