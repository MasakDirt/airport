from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import AirplaneType, Airplane, Airport, Route, Crew, Flight


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
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
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name",
        read_only=True
    )


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)


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

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")

    def validate(self, attrs: dict) -> dict:
        Flight.validate_time(
            departure_time=attrs["departure_time"],
            arrival_time=attrs["arrival_time"],
            error_to_raise=ValidationError
        )
        return attrs


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)


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
    _from = serializers.SlugRelatedField(
        source="route.source",
        slug_field="name",
        read_only=True
    )
    to = serializers.SlugRelatedField(
        source="route.destination",
        slug_field="name",
        read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "_from",
            "to",
            "airplane_name",
            "airplane_type",
            "departure_time",
            "arrival_time"
        )
