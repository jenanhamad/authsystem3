# Generated by Django 4.0.3 on 2022-03-04 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_submission_note_delete_note'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='type',
        ),
    ]