# Generated by Django 2.2.16 on 2022-07-17 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=256, verbose_name='имя категории'),
        ),
    ]
