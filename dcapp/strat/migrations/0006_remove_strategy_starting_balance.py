# Generated by Django 3.1 on 2020-09-14 12:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('strat', '0005_remove_strategy_position_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='strategy',
            name='starting_balance',
        ),
    ]
