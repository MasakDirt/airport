import datetime
from typing import Callable

from django.core.files.images import ImageFile
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_file_size(file: ImageFile, error_to_raise: Callable):
    if file:
        filesize = file.size
        max_upload_size = 1 * 1024 * 1024

        if filesize > max_upload_size:
            raise error_to_raise(
                _("The maximus image size that can be uploaded is 1 MB")
            )
        return file


def validate_time(
        departure_time: datetime,
        arrival_time: datetime,
        error_to_raise: Callable
) -> None:
    if departure_time > arrival_time:
        raise error_to_raise(
            _("Departure time cannot be later than arrival time")
        )


def validate_ticket(
        row: int,
        seat: int,
        airplane: models.Model,
        error_to_raise: Callable
) -> None:
    for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
        (row, "row", "rows"),
        (seat, "seat", "seats_in_row"),
    ]:
        airplane_attr_value = getattr(airplane, airplane_attr_name)
        if (0 < ticket_attr_value and
                ticket_attr_value > airplane_attr_value):
            raise error_to_raise(
                {
                    ticket_attr_name: _(
                        f"{ticket_attr_name} must be in range: "
                        f"(1, {airplane_attr_name})"
                        f"(1, {airplane_attr_value})"
                    )
                }
            )
