import datetime

from django.db.models import QuerySet, F, Count
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from airport.filters import FlightDateFilterBackend, RouteFilterBackend
from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Crew,
    Flight,
    Order,
)
from airport.ordering import MultipleOrdering
from airport.schemas import (
    flight_list_schema,
    airplane_list_schema,
    route_list_schema,
    order_list_schema,
)
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
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    AirplaneImageSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "airplane_type__name"]
    ordering_fields = ["name", "airplane_type__name"]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("flights")

            if self.action == "list":
                queryset = MultipleOrdering.perform_ordering(
                    request=self.request,
                    ordering_fields=self.ordering_fields,
                    queryset=queryset,
                )

        return queryset

    def get_serializer_class(self) -> ModelSerializer:
        serializer = super().get_serializer_class()
        if self.action == "list":
            serializer = AirplaneListSerializer
        elif self.action == "retrieve":
            serializer = AirplaneRetrieveSerializer
        elif self.action == "upload_image":
            serializer = AirplaneImageSerializer

        return serializer

    @airplane_list_schema()
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=True,
        url_name="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request: Request, pk: int) -> Response:
        airplane = get_object_or_404(Airplane, pk=pk)
        serializer = self.get_serializer(airplane, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "closest_big_city", ]

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
    filter_backends = [RouteFilterBackend, filters.SearchFilter]
    search_fields = [
        "source__name",
        "destination__name",
        "source__closest_big_city",
        "destination__closest_big_city",
    ]

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

    @route_list_schema()
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["last_name", "first_name"]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    filter_backends = [filters.SearchFilter, FlightDateFilterBackend]
    search_fields = [
        "route__source__name",
        "route__source__closest_big_city",
        "route__destination__name",
        "route__destination__closest_big_city",
        "airplane__name",
    ]
    ordering_fields = ["airplane__name", "departure_time", "arrival_time"]

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            departure_time__gte=datetime.datetime.now(datetime.UTC)
        )

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "airplane__airplane_type",
                "route__source",
                "route__destination",
            ).prefetch_related("crew")
            if self.action == "list":
                queryset = queryset.annotate(
                    tickets_available=(
                            F("airplane__rows") *
                            F("airplane__seats_in_row") - Count("tickets")
                    )
                ).order_by("id")

                queryset = MultipleOrdering.perform_ordering(
                    request=self.request,
                    ordering_fields=self.ordering_fields,
                    queryset=queryset,
                )

        return queryset

    def get_serializer_class(self) -> FlightSerializer:
        serializer = super().get_serializer_class()

        if self.action == "list":
            serializer = FlightListSerializer
        elif self.action == "retrieve":
            serializer = FlightDetailSerializer

        return serializer

    @flight_list_schema()
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "tickets__flight__route__source__name",
        "tickets__flight__route__source__closest_big_city",
        "tickets__flight__route__destination__name",
        "tickets__flight__route__destination__closest_big_city",
    ]
    ordering_fields = ["created_at"]

    def get_queryset(self) -> QuerySet[Order]:
        queryset = self.queryset.filter(user=self.request.user)

        if self.action in ("retrieve", "list"):
            queryset = queryset.prefetch_related(
                "tickets__flight__route__source",
                "tickets__flight__route__destination",
                "tickets__flight__crew",
                "tickets__flight__airplane__airplane_type",
            )

            if self.action == "list":
                queryset = MultipleOrdering.perform_ordering(
                    request=self.request,
                    ordering_fields=self.ordering_fields,
                    queryset=queryset,
                )

        return queryset

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)

    def get_serializer_class(self) -> ModelSerializer:
        serializer = super().get_serializer_class()

        if self.action == "list":
            serializer = OrderListSerializer
        elif self.action == "retrieve":
            serializer = OrderDetailSerializer

        return serializer

    @order_list_schema()
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)
