# Generated by Django 4.0.3 on 2022-03-13 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_host',
            field=models.BooleanField(default=True, verbose_name='Is host'),
        ),
    ]
