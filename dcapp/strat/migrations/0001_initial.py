# Generated by Django 3.1 on 2020-08-24 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Strategy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Confidence', models.TextField()),
                ('Risk', models.TextField()),
                ('Reward', models.TextField()),
                ('summary', models.TextField(default='POSITIVE MENTAL ATTITUDE!')),
            ],
        ),
    ]