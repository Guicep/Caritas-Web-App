# Generated by Django 5.0.4 on 2024-06-06 12:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('createuser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intercambio',
            name='fecha_acordada',
            field=models.DateField(default=datetime.date(2024, 6, 6)),
        ),
    ]
