# Generated by Django 5.1.1 on 2024-10-04 14:21

import airport.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airport', '0007_alter_flight_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airplane',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=airport.models.airplane_image),
        ),
    ]
