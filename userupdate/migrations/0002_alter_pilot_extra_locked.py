# Generated by Django 4.1 on 2022-08-09 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userupdate', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pilot',
            name='extra_locked',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]