# Generated by Django 2.1.7 on 2019-12-06 00:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0058_auto_20191205_1625'),
        ('users', '0192_auto_20191126_1800'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_amount', models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='EA Wallet')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.GameProvider')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='category',
            name='parent_id',
        ),
        migrations.RemoveField(
            model_name='game',
            name='category_id',
        ),
        migrations.RemoveField(
            model_name='game',
            name='status_id',
        ),
        migrations.DeleteModel(
            name='GameRequestsModel',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Game',
        ),
    ]
