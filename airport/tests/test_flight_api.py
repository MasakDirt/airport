import datetime

import pytz
from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Flight
from airport.serializers import FlightListSerializer, FlightDetailSerializer
from airport.tests.test_airplane_api import sample_airplane
from airport.tests.test_airplane_type_api import sample_airplane_type
from airport.tests.test_airport_api import sample_route, sample_airport
from airport.tests.test_crew_api import sample_crew


FLIGHT_URL = reverse("airport:flight-list")


def sample_flight(**additional) -> Flight:
    defaults = {
        "departure_time": datetime.datetime(2026, 12, 5),
        "arrival_time": datetime.datetime(2026, 12, 6, 12),
    }
    defaults.update(additional)

    return Flight.objects.create(**defaults)


def detail_url(flight_id: int) -> str:
    return reverse("airport:flight-detail", args=[flight_id])


def get_flight_data() -> dict:
    airport1 = sample_airport()
    airport2 = sample_airport(name="Airport #$2")
    route1 = sample_route(airport1, airport2)
    route2 = sample_route(airport2, airport1)

    airplane_type = sample_airplane_type(name="Airplane type 335")
    airplane1 = sample_airplane(airplane_type=airplane_type)
    airplane2 = sample_airplane(name="Air2", airplane_type=airplane_type)

    maks = sample_crew(first_name="Maks")
    user = sample_crew(first_name="User")

    return {
        "route1": route1,
        "route2": route2,
        "airplane1": airplane1,
        "airplane2": airplane2,
        "maks": maks,
        "user": user,
    }


class UnauthenticatedFlightTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(FLIGHT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_user(
                email="maksymkorniev88@gmail.com",
                password="ssAp@dr1AASow2"
            )
        )

    def test_flight_list(self):
        data = get_flight_data()

        maks = data["maks"]
        user = data["user"]

        flight1 = sample_flight(
            route=data["route1"], airplane=data["airplane1"]
        )
        flight2 = sample_flight(
            route=data["route2"], airplane=data["airplane2"]
        )

        flight1.crew.add(maks, user)
        flight2.crew.add(user, maks)

        response = self.client.get(FLIGHT_URL)

        flights = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") - Count("tickets")
            )
        ).order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for flight in response.data["results"]:
            self.assertIn(flight, serializer.data)

    def test_flight_ordering(self):
        data = get_flight_data()

        maks = data["maks"]
        user = data["user"]

        flight1 = sample_flight(
            route=data["route1"],
            airplane=data["airplane1"]
        )
        flight2 = sample_flight(
            route=data["route2"],
            airplane=data["airplane2"]
        )
        flight3 = sample_flight(
            route=data["route2"],
            airplane=data["airplane1"]
        )
        flight4 = sample_flight(
            route=data["route1"],
            airplane=data["airplane2"],
            departure_time=datetime.datetime(2026, 12, 6, 8)
        )

        flight1.crew.add(maks, user)
        flight3.crew.add(user, maks)
        flight2.crew.add(user, maks)
        flight4.crew.add(user, maks)

        ordering = "departure_time,airplane__name"

        response = self.client.get(FLIGHT_URL, {"ordering": ordering})

        orders = (order for order in ordering.split(","))
        flights = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") - Count("tickets")
            )
        ).order_by(*orders)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for flight in response.data["results"]:
            self.assertIn(flight, serializer.data)

    def test_flight_filter_by_departure_day(self):
        data = get_flight_data()

        maks = data["maks"]
        user = data["user"]

        flight1 = sample_flight(
            route=data["route1"],
            airplane=data["airplane1"]
        )
        flight2 = sample_flight(
            route=data["route2"],
            airplane=data["airplane2"]
        )
        flight3 = sample_flight(
            route=data["route2"],
            airplane=data["airplane1"],
            departure_time=datetime.datetime(2026, 12, 4)
        )
        flight4 = sample_flight(
            route=data["route1"],
            airplane=data["airplane2"],
            departure_time=datetime.datetime(2026, 12, 6)
        )

        flight1.crew.add(maks, user)
        flight3.crew.add(user, maks)
        flight2.crew.add(user, maks)
        flight4.crew.add(user, maks)

        departure_date = datetime.date(2026, 12, 5)

        response = self.client.get(
            FLIGHT_URL,
            {"departure_day": departure_date}
        )

        flights = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") - Count("tickets")
            )
        ).order_by("id").filter(departure_time__date=departure_date)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_filter_by_arrival_day(self):
        data = get_flight_data()

        maks = data["maks"]
        user = data["user"]

        flight1 = sample_flight(
            route=data["route1"],
            airplane=data["airplane1"]
        )
        flight2 = sample_flight(
            route=data["route2"],
            airplane=data["airplane2"]
        )
        flight3 = sample_flight(
            route=data["route2"],
            airplane=data["airplane1"],
            arrival_time=datetime.datetime(2026, 12, 7)
        )
        flight4 = sample_flight(
            route=data["route1"],
            airplane=data["airplane2"],
            arrival_time=datetime.datetime(2026, 12, 7)
        )

        flight1.crew.add(maks, user)
        flight3.crew.add(user, maks)
        flight2.crew.add(user, maks)
        flight4.crew.add(user, maks)

        arrival_day = datetime.date(2026, 12, 7)

        response = self.client.get(
            FLIGHT_URL,
            {"arrival_day": arrival_day}
        )

        flights = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") - Count("tickets")
            )
        ).order_by("id").filter(arrival_time__date=arrival_day)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_filter_by_departure_start(self):
        data = get_flight_data()

        maks = data["maks"]
        user = data["user"]

        flight1 = sample_flight(
            route=data["route1"],
            airplane=data["airplane1"]
        )
        flight2 = sample_flight(
            route=data["route2"],
            airplane=data["airplane2"]
        )
        flight3 = sample_flight(
            route=data["route2"],
            airplane=data["airplane1"],
            departure_time=datetime.datetime(2026, 12, 1),
            arrival_time=datetime.datetime(2026, 12, 2),
        )
        flight4 = sample_flight(
            route=data["route1"],
            airplane=data["airplane2"],
            departure_time=datetime.datetime(2026, 12, 4)
        )

        flight1.crew.add(maks, user)
        flight3.crew.add(user, maks)
        flight2.crew.add(user, maks)
        flight4.crew.add(user, maks)

        departure_start = datetime.date(2026, 12, 3)

        response = self.client.get(
            FLIGHT_URL,
            {"departure_start": departure_start}
        )

        flights = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") - Count("tickets")
            )
        ).order_by("id").filter(departure_time__gte=departure_start)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for flight in response.data["results"]:
            self.assertIn(flight, serializer.data)

    def test_flight_filter_by_arriving_start(self):
        data = get_flight_data()

        maks = data["maks"]
        user = data["user"]

        flight1 = sample_flight(
            route=data["route1"],
            airplane=data["airplane1"]
        )
        flight2 = sample_flight(
            route=data["route2"],
            airplane=data["airplane2"]
        )
        flight3 = sample_flight(
            route=data["route2"],
            airplane=data["airplane1"],
            departure_time=datetime.datetime(2026, 12, 1),
            arrival_time=datetime.datetime(2026, 12, 2),
        )
        flight4 = sample_flight(
            route=data["route1"],
            airplane=data["airplane2"],
            arrival_time=datetime.datetime(2026, 12, 8)
        )

        flight1.crew.add(maks, user)
        flight3.crew.add(user, maks)
        flight2.crew.add(user, maks)
        flight4.crew.add(user, maks)

        arriving_start = datetime.date(2026, 12, 6)

        response = self.client.get(
            FLIGHT_URL,
            {"arriving_start": arriving_start}
        )

        flights = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") - Count("tickets")
            )
        ).order_by("id").filter(arrival_time__gte=arriving_start)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for flight in response.data["results"]:
            self.assertIn(flight, serializer.data)

    def test_flight_filter_by_departure_end(self):
        data = get_flight_data()

        maks = data["maks"]
        user = data["user"]

        flight1 = sample_flight(
            route=data["route1"],
            airplane=data["airplane1"]
        )
        flight2 = sample_flight(
            route=data["route2"],
            airplane=data["airplane2"]
        )
        flight3 = sample_flight(
            route=data["route2"],
            airplane=data["airplane1"],
            departure_time=datetime.datetime(2026, 12, 1),
            arrival_time=datetime.datetime(2026, 12, 2),
        )
        flight4 = sample_flight(
            route=data["route1"],
            airplane=data["airplane2"],
            departure_time=datetime.datetime(2026, 12, 4)
        )

        flight1.crew.add(maks, user)
        flight3.crew.add(user, maks)
        flight2.crew.add(user, maks)
        flight4.crew.add(user, maks)

        departure_end = datetime.date(2026, 12, 5)

        response = self.client.get(
            FLIGHT_URL,
            {"departure_end": departure_end}
        )

        flights = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") - Count("tickets")
            )
        ).order_by("id").filter(departure_time__lte=departure_end)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for flight in response.data["results"]:
            self.assertIn(flight, serializer.data)

    def test_flight_filter_by_arriving_end(self):
        data = get_flight_data()

        maks = data["maks"]
        user = data["user"]

        flight1 = sample_flight(
            route=data["route1"],
            airplane=data["airplane1"]
        )
        flight2 = sample_flight(
            route=data["route2"],
            airplane=data["airplane2"]
        )
        flight3 = sample_flight(
            route=data["route2"],
            airplane=data["airplane1"],
            departure_time=datetime.datetime(2026, 12, 1),
            arrival_time=datetime.datetime(2026, 12, 2),
        )
        flight4 = sample_flight(
            route=data["route1"],
            airplane=data["airplane2"],
            departure_time=datetime.datetime(2026, 12, 9),
            arrival_time=datetime.datetime(2026, 12, 10)
        )

        flight1.crew.add(maks, user)
        flight3.crew.add(user, maks)
        flight2.crew.add(user, maks)
        flight4.crew.add(user, maks)

        arriving_end = datetime.date(2026, 12, 8)

        response = self.client.get(
            FLIGHT_URL,
            {"arriving_end": arriving_end}
        )

        flights = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") - Count("tickets")
            )
        ).order_by("id").filter(arrival_time__lte=arriving_end)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for flight in response.data["results"]:
            self.assertIn(flight, serializer.data)

    def test_flight_filter_by_departure_start_and_arriving_end(self):
        data = get_flight_data()

        flight1 = sample_flight(
            route=data["route1"],
            airplane=data["airplane1"]
        )
        flight2 = sample_flight(
            route=data["route2"],
            airplane=data["airplane2"]
        )
        flight3 = sample_flight(
            route=data["route2"],
            airplane=data["airplane1"],
            departure_time=datetime.datetime(2026, 12, 8),
            arrival_time=datetime.datetime(2026, 12, 9),
        )
        flight4 = sample_flight(
            route=data["route1"],
            airplane=data["airplane2"],
            departure_time=datetime.datetime(2026, 12, 9),
            arrival_time=datetime.datetime(2026, 12, 10)
        )

        maks = data["maks"]
        user = data["user"]

        flight1.crew.add(maks, user)
        flight3.crew.add(user, maks)
        flight2.crew.add(user, maks)
        flight4.crew.add(user, maks)

        departure_start = datetime.date(2026, 12, 8)
        arriving_end = datetime.date(2026, 12, 11)

        response = self.client.get(
            FLIGHT_URL,
            {
                "departure_start": departure_start,
                "arriving_end": arriving_end,
            }
        )

        flights = Flight.objects.annotate(
            tickets_available=(
                    F("airplane__rows") *
                    F("airplane__seats_in_row") - Count("tickets")
            )
        ).order_by("id").filter(
            departure_time__gte=departure_start,
            arrival_time__lte=arriving_end
        )
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for flight in response.data["results"]:
            self.assertIn(flight, serializer.data)

    def test_flight_detail(self):
        airport1 = sample_airport()
        airport2 = sample_airport(name="Airport #$2")
        route1 = sample_route(airport1, airport2)

        airplane_type = sample_airplane_type(name="Airplane type #35")
        airplane1 = sample_airplane(airplane_type=airplane_type)

        maks = sample_crew(first_name="Maks")
        user = sample_crew(first_name="User")

        flight = sample_flight(route=route1, airplane=airplane1)

        flight.crew.add(maks, user)

        response = self.client.get(detail_url(flight.id))

        serializer = FlightDetailSerializer(flight)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_flight_create_forbidden(self):
        data = get_flight_data()
        payload = {
            "departure_time": datetime.datetime(2026, 12, 5),
            "arrival_time": datetime.datetime(2026, 12, 6, 12),
            "airplane": data["airplane1"],
            "route": data["route2"],
            "crew": [data["maks"].id, data["user"].id]
        }

        response = self.client.post(FLIGHT_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_superuser(
                email="flight_admin@mail.co",
                password="onew@sdao09i4r474rwedA"
            )
        )

    def test_create_flight(self):
        data = get_flight_data()
        utc = pytz.UTC
        payload = {
            "departure_time": datetime.datetime(2026, 12, 5, tzinfo=utc),
            "arrival_time": datetime.datetime(2026, 12, 6, 12, tzinfo=utc),
            "airplane": data["airplane1"].id,
            "route": data["route2"].id,
            "crew": [data["maks"].id, data["user"].id]
        }

        response = self.client.post(FLIGHT_URL, data=payload)

        crew = Flight.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            payload["departure_time"],
            getattr(crew, "departure_time")
        )
        self.assertEqual(
            payload["arrival_time"],
            getattr(crew, "arrival_time")
        )
        self.assertEqual(
            payload["airplane"],
            getattr(crew, "airplane").id
        )
        self.assertEqual(
            payload["route"],
            getattr(crew, "route").id
        )
        for crew in getattr(crew, "crew").all():
            self.assertIn(crew.id, payload["crew"])
