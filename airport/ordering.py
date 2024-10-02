from django.db.models import QuerySet
from rest_framework.request import Request


class MultipleOrdering:
    ordering_param = "ordering"
    default_param = "-pk"

    @classmethod
    def _get_values_from_query(cls, query_params: dict) -> list[str]:
        ordering = query_params.get(cls.ordering_param, cls.default_param)
        return ordering.split(",")

    @classmethod
    def _get_all_possible_fields(cls, starting_fields: list[str]) -> set[str]:
        return set(
            ["-" + field for field in starting_fields] +
            starting_fields
        )

    @classmethod
    def _get_ordering_fields(
            cls, request: Request,
            fields: list[str]
    ) -> list[str]:
        ordering_fields = cls._get_values_from_query(request.query_params)
        all_fields = cls._get_all_possible_fields(fields)
        proceed_ordering = [
            field
            for field in ordering_fields
            if field in all_fields
        ]

        if not proceed_ordering:
            return [cls.default_param]

        return proceed_ordering

    @classmethod
    def perform_ordering(
            cls, request: Request,
            ordering_fields: list[str],
            queryset: QuerySet
    ) -> QuerySet:
        if "ordering" in request.query_params:
            ordering = cls._get_ordering_fields(
                request,
                ordering_fields
            )
            return queryset.order_by(*ordering)

        return queryset
