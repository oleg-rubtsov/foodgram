# Generated by Django 2.2.19 on 2022-01-12 14:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_auto_20220111_1824'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='owner',
            new_name='author',
        ),
    ]
