# Generated by Django 3.1.6 on 2021-03-31 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20210331_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commandexecution',
            name='result',
            field=models.CharField(default='Processing', max_length=250),
        ),
        migrations.AlterField(
            model_name='commandexecution',
            name='state',
            field=models.CharField(default='Created', max_length=250),
        ),
    ]
