import os

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from airport.models import Airplane


@receiver(pre_delete, sender=Airplane)
def delete_image(sender, instance, **kwargs):
    if os.path.isfile(instance.image.path):
        os.remove(instance.image.path)
