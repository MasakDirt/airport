import os
import uuid

from django.db import models
from django.utils.text import slugify


def airplane_image(instance: models.Model, filename: str) -> str:
    filename, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}-{filename}{extension}"

    return os.path.join("uploads/airplanes/", filename)
