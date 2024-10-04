import os.path
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify

from airport.validators import (
    validate_time,
    validate_file_size,
    validate_ticket,
)


class AirplaneType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "airplane type"

    def __str__(self) -> str:
        return self.name


def airplane_image(instance: "Airplane", filename: str) -> str:
    filename, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}-{filename}{extension}"

    return os.path.join("uploads/airplanes/", filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    image = models.ImageField(blank=True, null=True, upload_to=airplane_image)
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return str(
            f"Airplane - {self.name} (capacity - "
            f"{self.capacity}, type - {self.airplane_type})"
        )

    def clean(self):
        validate_file_size(
            file=self.image,
            error_to_raise=ValidationError
        )

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super().save(
            *args,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Airport - {self.name}, closest to {self.closest_big_city}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_to"
    )
    distance = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"Route {self.source.name} -- {self.destination.name}"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["source", "destination"],
                name="route_unique_source_and_destination"
            )
        ]


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.full_name


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ("departure_time",)

    def __str__(self) -> str:
        return (f"{self.route} - {self.airplane.name}, "
                f"{self.departure_time.strftime('%d %b %y %H:%M')} - "
                f"{self.arrival_time.strftime('%d %b %y %H:%M')}")

    def clean(self):
        validate_time(
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            error_to_raise=ValidationError
        )

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super().save(
            *args,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "flight"],
                name="ticket_unique_row_and_seat"
            )
        ]

    def __str__(self) -> str:
        return str(
            f"{self.order.user.username} ticket "
            f"for (row - {self.row}, seat - {self.seat})"
        )

    def clean(self) -> None:
        validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
            self, *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super().save(
            *args,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.user.username} order"
