from rest_framework import serializers

from airport.models import AirplaneType, Airplane, Airport, Route, Crew


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
