# Generated by Django 3.1.6 on 2021-04-29 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20210428_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='modulevalue',
            name='unit',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
    ]
