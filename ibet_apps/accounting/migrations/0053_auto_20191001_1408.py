# Generated by Django 2.1.7 on 2019-10-01 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0052_merge_20190917_1038'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DepositReview',
        ),
        migrations.DeleteModel(
            name='WithdrawReview',
        ),
        migrations.AddField(
            model_name='transaction',
            name='supplier',
            field=models.CharField(max_length=50, null=True, verbose_name='Supplier'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='remark',
            field=models.CharField(blank=True, max_length=200, verbose_name='Details'),
        ),
    ]