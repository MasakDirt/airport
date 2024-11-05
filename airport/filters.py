from django.db.models import QuerySet
from rest_framework import filters
from rest_framework.request import Request
from rest_framework.views import APIView


def _perform_filtering(
        filter_value: str,
        filter_field: str,
        queryset: QuerySet
) -> QuerySet:
    if filter_value:
        queryset = queryset.filter(**{filter_field: filter_value})

    return queryset


class FlightDateFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(
            self, request: Request,
            queryset: QuerySet,
            view: APIView
    ) -> QuerySet:
        departure_day = request.query_params.get("departure_day")
        arrival_day = request.query_params.get("arrival_day")
        departure_start = request.query_params.get("departure_start")
        arriving_start = request.query_params.get("arriving_start")
        departure_end = request.query_params.get("departure_end")
        arriving_end = request.query_params.get("arriving_end")

        queryset = _perform_filtering(
            filter_value=departure_day,
            filter_field="departure_time__date",
            queryset=queryset
        )

        queryset = _perform_filtering(
            filter_value=arrival_day,
            filter_field="arrival_time__date",
            queryset=queryset
        )

        queryset = _perform_filtering(
            filter_value=departure_start,
            filter_field="departure_time__gte",
            queryset=queryset
        )

        queryset = _perform_filtering(
            filter_value=arriving_start,
            filter_field="arrival_time__gte",
            queryset=queryset
        )

        queryset = _perform_filtering(
            filter_value=departure_end,
            filter_field="departure_time__lte",
            queryset=queryset
        )

        queryset = _perform_filtering(
            filter_value=arriving_end,
            filter_field="arrival_time__lte",
            queryset=queryset
        )

        return queryset.order_by("departure_time")


class RouteFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(
            self, request: Request,
            queryset: QuerySet,
            view: APIView
    ) -> QuerySet:
        source_city = request.query_params.get("s_city")
        destination_city = request.query_params.get("d_city")
        source_airport = request.query_params.get("s_airport")
        destination_airport = request.query_params.get("d_airport")

        queryset = _perform_filtering(
            filter_value=source_city,
            filter_field="source__closest_big_city__icontains",
            queryset=queryset
        )

        queryset = _perform_filtering(
            filter_value=destination_city,
            filter_field="destination__closest_big_city__icontains",
            queryset=queryset
        )

        queryset = _perform_filtering(
            filter_value=source_airport,
            filter_field="source__name__icontains",
            queryset=queryset
        )

        queryset = _perform_filtering(
            filter_value=destination_airport,
            filter_field="destination__name__icontains",
            queryset=queryset
        )

        return queryset
