# Generated by Django 2.1.7 on 2019-10-16 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0166_merge_20191016_0020'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ReferLink',
            new_name='ReferChannel',
        ),
        migrations.RenameField(
            model_name='referchannel',
            old_name='refer_link_name',
            new_name='refer_channel_name',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='referral_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='referchannel',
            unique_together={('user_id', 'refer_channel_name')},
        ),
    ]