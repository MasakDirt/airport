# Generated by Django 5.1.1 on 2024-09-30 18:11

import airport.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airport', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='airplane',
            name='image',
            field=models.ImageField(null=True, upload_to=airport.models.airplane_image),
        ),
    ]
