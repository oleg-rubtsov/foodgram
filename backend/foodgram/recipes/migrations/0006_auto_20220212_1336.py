# Generated by Django 2.2.19 on 2022-02-12 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20220212_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=50, verbose_name='ingredient_name'),
        ),
    ]
