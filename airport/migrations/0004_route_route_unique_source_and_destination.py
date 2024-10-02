# Generated by Django 5.1.1 on 2024-09-30 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airport', '0003_airplane_image'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='route',
            constraint=models.UniqueConstraint(fields=('source', 'destination'), name='route_unique_source_and_destination'),
        ),
    ]