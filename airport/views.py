from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer

from airport.models import AirplaneType, Airplane
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer
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
