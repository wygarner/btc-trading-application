# Generated by Django 3.1 on 2020-08-29 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strat', '0003_auto_20200826_1402'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='strategy',
            name='long_entries',
        ),
        migrations.RemoveField(
            model_name='strategy',
            name='short_entries',
        ),
        migrations.RemoveField(
            model_name='strategy',
            name='stops',
        ),
        migrations.AddField(
            model_name='strategy',
            name='position_size',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='strategy',
            name='starting_balance',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
    ]
