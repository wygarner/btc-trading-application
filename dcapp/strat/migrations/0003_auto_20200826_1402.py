# Generated by Django 3.1 on 2020-08-26 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strat', '0002_auto_20200824_1722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='strategy',
            name='summary',
        ),
        migrations.AddField(
            model_name='strategy',
            name='long_entries',
            field=models.TextField(default='market'),
        ),
        migrations.AddField(
            model_name='strategy',
            name='short_entries',
            field=models.TextField(default='market'),
        ),
        migrations.AddField(
            model_name='strategy',
            name='stops',
            field=models.TextField(default='market'),
        ),
    ]
