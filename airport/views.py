from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer

from airport.models import AirplaneType, Airplane, Airport, Route
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    AirportDetailSerializer,
    RouteDetailSerializer
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

    def get_serializer_class(self) -> ModelSerializer:
        serializer = super().get_serializer_class()

        if self.action == "retrieve":
            serializer = AirportDetailSerializer

        return serializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self) -> RouteSerializer:
        serializer = super().get_serializer_class()

        if self.action == "list":
            serializer = RouteListSerializer
        elif self.action == "retrieve":
            serializer = RouteDetailSerializer

        return serializer
