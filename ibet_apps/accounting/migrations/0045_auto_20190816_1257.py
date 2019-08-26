# Generated by Django 2.1.7 on 2019-08-16 19:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [("accounting", "0044_auto_20190813_1542")]

    operations = [
        migrations.CreateModel(
            name="Bank",
            fields=[
                (
                    "bank_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(default=0, max_length=200)),
                (
                    "province",
                    models.CharField(blank=True, default=0, max_length=200, null=True),
                ),
                (
                    "city",
                    models.CharField(blank=True, default=0, max_length=200, null=True),
                ),
                (
                    "branch",
                    models.CharField(blank=True, default=0, max_length=200, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BankAccount",
            fields=[
                (
                    "account_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("account_name", models.CharField(default=0, max_length=200)),
                ("account_number", models.CharField(default=0, max_length=200)),
                (
                    "bank",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounting.Bank",
                    ),
                ),
            ],
        ),
        migrations.RemoveField(model_name="transaction", name="bank"),
        migrations.RemoveField(model_name="transaction", name="payer_id"),
        migrations.AddField(
            model_name="depositchannel",
            name="block_risk_level",
            field=models.SmallIntegerField(
                choices=[(0, "A"), (1, "E1"), (2, "E2"), (3, "F")], default=0
            ),
        ),
        migrations.AddField(
            model_name="depositchannel",
            name="limit_access",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="depositchannel",
            name="new_user_volume",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=20),
        ),
        migrations.AddField(
            model_name="depositchannel",
            name="transaction_fee",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                max_digits=20,
                verbose_name="Transaction Fee",
            ),
        ),
        migrations.AddField(
            model_name="depositchannel",
            name="volume",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=20),
        ),
        migrations.AddField(
            model_name="transaction",
            name="transaction_image",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name="withdrawchannel",
            name="block_risk_level",
            field=models.SmallIntegerField(
                choices=[(0, "A"), (1, "E1"), (2, "E2"), (3, "F")], default=0
            ),
        ),
        migrations.AddField(
            model_name="withdrawchannel",
            name="limit_access",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="withdrawchannel",
            name="new_user_volume",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=20),
        ),
        migrations.AddField(
            model_name="withdrawchannel",
            name="volume",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=20),
        ),
        migrations.RemoveField(model_name="depositchannel", name="switch"),
        migrations.AddField(
            model_name="depositchannel",
            name="switch",
            field=models.SmallIntegerField(
                choices=[(0, "OPEN"), (1, "CLOSE")], default=0
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="arrive_time",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Account Time"
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="currency",
            field=models.SmallIntegerField(
                choices=[
                    (0, "CNY"),
                    (1, "USD"),
                    (2, "THB"),
                    (3, "IDR"),
                    (4, "HKD"),
                    (5, "AUD"),
                    (6, "THB"),
                    (7, "MYR"),
                    (8, "VND"),
                    (9, "MMK"),
                    (10, "XBT"),
                ],
                default=0,
                verbose_name="Currency",
            ),
        ),
        migrations.RemoveField(model_name="withdrawchannel", name="switch"),
        migrations.AddField(
            model_name="withdrawchannel",
            name="switch",
            field=models.SmallIntegerField(
                choices=[(0, "OPEN"), (1, "CLOSE")], default=0
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="user_bank_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="accounting.BankAccount",
            ),
        ),
    ]
