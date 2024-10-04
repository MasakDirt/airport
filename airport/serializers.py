from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Crew,
    Flight,
    Ticket,
    Order,
)
from airport.validators import (
    validate_time,
    validate_ticket,
    validate_file_size,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    used_in_flights = serializers.IntegerField(
        source="flights.count",
        read_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "image",
            "used_in_flights",
        )
        read_only_fields = ("id", "image")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name",
        read_only=True
    )


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("image",)

    def validate(self, attrs: dict) -> dict:
        validate_file_size(
            file=attrs["image"],
            error_to_raise=ValidationError
        )

        return attrs


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirportDetailSerializer(serializers.ModelSerializer):
    depart_for = serializers.SerializerMethodField(read_only=True)
    accepts_from = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "closest_big_city",
            "depart_for",
            "accepts_from"
        )

    def get_depart_for(self, obj: Airport) -> list[str]:
        return [route.destination.name for route in obj.routes_from.all()]

    def get_accepts_from(self, obj: Airport) -> list[str]:
        return [route.source.name for route in obj.routes_to.all()]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.select_related("source", "destination")
    )
    airplane = serializers.PrimaryKeyRelatedField(
        queryset=Airplane.objects.select_related("airplane_type")
    )
    departure_time = serializers.DateTimeField(format="%d %B %y %H:%M")
    arrival_time = serializers.DateTimeField(format="%d %B %y %H:%M")

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )

    def validate(self, attrs: dict) -> dict:
        validate_time(
            departure_time=attrs["departure_time"],
            arrival_time=attrs["arrival_time"],
            error_to_raise=ValidationError
        )
        return attrs


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    taken_places = serializers.SerializerMethodField()

    class Meta:
        model = FlightSerializer.Meta.model
        fields = FlightSerializer.Meta.fields + ("taken_places",)

    def get_taken_places(self, obj: Flight) -> list[dict]:
        return [
            {"row": ticket.row, "seat": ticket.seat}
            for ticket in obj.tickets.all()
        ]


class FlightListSerializer(serializers.ModelSerializer):
    airplane_name = serializers.SlugRelatedField(
        source="airplane",
        slug_field="name",
        read_only=True
    )
    airplane_type = serializers.SlugRelatedField(
        source="airplane.airplane_type",
        slug_field="name",
        read_only=True
    )
    out_of = serializers.SlugRelatedField(
        source="route.source",
        slug_field="name",
        read_only=True
    )
    to = serializers.SlugRelatedField(
        source="route.destination",
        slug_field="name",
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)
    crew = serializers.SlugRelatedField(
        many=True,
        slug_field="full_name",
        read_only=True
    )
    departure_time = serializers.DateTimeField(format="%d %B %y %H:%M")
    arrival_time = serializers.DateTimeField(format="%d %B %y %H:%M")

    class Meta:
        model = Flight
        fields = (
            "id",
            "out_of",
            "to",
            "airplane_name",
            "airplane_type",
            "departure_time",
            "arrival_time",
            "tickets_available",
            "crew"
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")

    def validate(self, attrs):
        validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError,
        )
        return attrs


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)


class TicketDetailSerializer(TicketSerializer):
    flight = FlightDetailSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)
    created_at = serializers.DateTimeField(
        format="%d %B %y %H:%M",
        read_only=True
    )

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data: dict) -> Order:
        tickets_data = validated_data.pop("tickets")
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)

            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderListSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)
