# Generated by Django 3.1 on 2020-08-24 17:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('strat', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='strategy',
            old_name='Confidence',
            new_name='confidence',
        ),
        migrations.RenameField(
            model_name='strategy',
            old_name='Reward',
            new_name='reward',
        ),
        migrations.RenameField(
            model_name='strategy',
            old_name='Risk',
            new_name='risk',
        ),
    ]
