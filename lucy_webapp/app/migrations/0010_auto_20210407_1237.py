# Generated by Django 3.1.7 on 2021-04-07 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_commandexecution_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commandexecution',
            name='timestamp',
            field=models.BigIntegerField(),
        ),
    ]
