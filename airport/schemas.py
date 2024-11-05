from typing import Callable

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample
)
import datetime


def flight_list_schema() -> Callable:
    def decorator(func: Callable):
        return extend_schema(
            parameters=[
                OpenApiParameter(
                    "departure_day",
                    type=str,
                    description="Find all flights at selected departure day",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample(
                            "today",
                            value=str(datetime.date.today())
                        ),
                        OpenApiExample("27 October", value="2024-10-27"),
                    ]
                ),
                OpenApiParameter(
                    "arrival_day",
                    type=str,
                    description="Find all flights at selected arrival day",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample(
                            "today",
                            value=str(datetime.date.today())
                        ),
                        OpenApiExample("28 October", value="2024-10-28"),
                    ]
                ),
                OpenApiParameter(
                    "departure_start",
                    type=str,
                    description="Find all flights departure time that "
                                "will fly after selected date",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample(
                            "today",
                            value=str(datetime.date.today())
                        ),
                        OpenApiExample("16 October", value="2024-10-16"),
                    ]
                ),
                OpenApiParameter(
                    "arriving_start",
                    type=str,
                    description="Find all flights arriving time that "
                                "will fly after selected date",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample(
                            "today",
                            value=str(datetime.date.today())
                        ),
                        OpenApiExample("16 October", value="2024-10-16"),
                    ]
                ),
                OpenApiParameter(
                    "departure_end",
                    type=str,
                    description="Find all flights departure time that "
                                "will fly before selected date",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample(
                            "today",
                            value=str(datetime.date.today())
                        ),
                        OpenApiExample("1 November", value="2024-11-01"),
                    ]
                ),
                OpenApiParameter(
                    "arriving_end",
                    type=str,
                    description="Find all flights arriving time that "
                                "will fly before selected date",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample(
                            "today",
                            value=str(datetime.date.today())
                        ),
                        OpenApiExample("28 October", value="2024-10-28"),
                    ]
                ),
                OpenApiParameter(
                    "ordering",
                    type={"type": "list", "items": {"type": "str"}},
                    description="Order flights by different "
                                "fields (airplane name, "
                                "departure time, arrival time)",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample(
                            "airplane name (ASC)",
                            value="airplane__name"
                        ),
                        OpenApiExample(
                            "airplane name (DESC)",
                            value="-airplane__name"
                        ),
                        OpenApiExample(
                            "departure time (ASC)",
                            value="departure_time"
                        ),
                        OpenApiExample(
                            "departure time (DESC)",
                            value="-departure_time"
                        ),
                        OpenApiExample(
                            "arrival time (ASC)",
                            value="arrival_time"
                        ),
                        OpenApiExample(
                            "arrival time (DESC)",
                            value="-arrival_time"
                        ),
                        OpenApiExample(
                            "arrival time and airplane name (ASC)",
                            value="arrival_time,airplane__name"
                        ),
                    ]
                ),
            ]
        )(func)

    return decorator


def route_list_schema() -> Callable:
    def decorator(func: Callable):
        return extend_schema(
            parameters=[
                OpenApiParameter(
                    "s_city",
                    type=str,
                    description="Find all source airports "
                                "which fly from this city",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample("London", value="London"),
                        OpenApiExample("partial London", value="lond"),
                    ]
                ),
                OpenApiParameter(
                    "d_city",
                    type=str,
                    description="Find all departure airports "
                                "which fly to this city",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample("Paris", value="Paris"),
                        OpenApiExample("partial Paris", value="par"),
                    ]
                ),
                OpenApiParameter(
                    "s_airport",
                    type=str,
                    description="Find all source airports "
                                "with appropriate name",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample(
                            "San Francisco International Airport",
                            value="San Francisco International Airport"
                        ),
                        OpenApiExample(
                            "San Francisco International Airport partial",
                            value="san francisco"
                        ),
                    ]
                ),
                OpenApiParameter(
                    "d_airport",
                    type=str,
                    description="Find all departure airports "
                                "with appropriate name",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample(
                            "Dubai International Airport",
                            value="Dubai International Airport"
                        ),
                        OpenApiExample(
                            "Dubai International Airport partial",
                            value="dubai"
                        ),
                    ]
                ),
            ]
        )(func)

    return decorator


def airplane_list_schema() -> Callable:
    def decorator(func: Callable):
        return extend_schema(
            parameters=[
                OpenApiParameter(
                    "ordering",
                    type={"type": "list", "items": {"type": "str"}},
                    description="Order airplanes by specific "
                                "parameters (name, airplane_type_name)",
                    required=False,
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample("order by name (ASC)", value="name"),
                        OpenApiExample("order by name (DESC)", value="-name"),
                        OpenApiExample(
                            "order by airplane type name (ASC)",
                            value="airplane_type__name"
                        ),
                        OpenApiExample(
                            "order by airplane type name (DESC)",
                            value="-airplane_type__name"
                        ),
                        OpenApiExample(
                            "order by airplane type "
                            "name (DESC) and name (ASC)",
                            value="-airplane_type__name,name"
                        ),
                    ]
                )
            ]
        )(func)

    return decorator


def order_list_schema() -> Callable:
    def decorator(func: Callable):
        return extend_schema(
            parameters=[
                OpenApiParameter(
                    "ordering",
                    type={"type": "list", "items": {"type": "str"}},
                    description="Order flights by created at",
                    examples=[
                        OpenApiExample("", value=""),
                        OpenApiExample("created at (ASC)", value="created_at"),
                        OpenApiExample(
                            "created at (DESC)",
                            value="-created_at"
                        ),
                    ]
                ),
            ]
        )(func)

    return decorator
