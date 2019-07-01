# Generated by Django 2.1.7 on 2019-06-21 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0101_auto_20190620_2237'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='address',
            new_name='street_address',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='language',
            field=models.CharField(choices=[('English', 'English'), ('Chinese', 'Chinese'), ('French', 'French')], default='English', max_length=20),
        ),
    ]