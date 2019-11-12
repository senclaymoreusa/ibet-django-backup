# Generated by Django 2.1.7 on 2019-10-28 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0172_merge_20191028_1520'),
    ]

    operations = [
        migrations.CreateModel(
            name='Segmentation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('turnover_threshold', models.DecimalField(decimal_places=2, max_digits=20)),
                ('annual_threshold', models.DecimalField(decimal_places=2, max_digits=20)),
                ('platform_turnover_daily', models.DecimalField(decimal_places=2, max_digits=20)),
                ('deposit_amount_daily', models.DecimalField(decimal_places=2, max_digits=20)),
                ('deposit_amount_monthly', models.DecimalField(decimal_places=2, max_digits=20)),
                ('general_bonuses', models.BooleanField(default=False)),
                ('product_turnover_bonuses', models.BooleanField(default=False)),
            ],
        ),
    ]