from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer

from airport.models import AirplaneType, Airplane, Airport, Route, Crew, Flight
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    AirportDetailSerializer,
    RouteDetailSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightDetailSerializer,
    FlightListSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer

    def get_serializer_class(self) -> ModelSerializer:
        serializer = super().get_serializer_class()
        if self.action == "list":
            serializer = AirplaneListSerializer
        elif self.action == "retrieve":
            serializer = AirplaneRetrieveSerializer

        return serializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self) -> QuerySet[Airport]:
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "routes_from__destination",
                "routes_to__source",
            )

        return queryset

    def get_serializer_class(self) -> ModelSerializer:
        serializer = super().get_serializer_class()

        if self.action == "retrieve":
            serializer = AirportDetailSerializer

        return serializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self) -> QuerySet[Flight]:
        queryset = super().get_queryset()

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("source", "destination")

        return queryset

    def get_serializer_class(self) -> RouteSerializer:
        serializer = super().get_serializer_class()

        if self.action == "list":
            serializer = RouteListSerializer
        elif self.action == "retrieve":
            serializer = RouteDetailSerializer

        return serializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "airplane__airplane_type",
                "route__source",
                "route__destination",
            )

        return queryset

    def get_serializer_class(self) -> FlightSerializer:
        serializer = super().get_serializer_class()

        if self.action == "list":
            serializer = FlightListSerializer
        elif self.action == "retrieve":
            serializer = FlightDetailSerializer

        return serializer
