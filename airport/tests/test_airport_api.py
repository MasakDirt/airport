from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Route
from airport.serializers import AirportSerializer, AirportDetailSerializer

AIRPORT_URL = reverse("airport:airport-list")


def sample_route(airport1: Airport, airport2: Airport) -> Route:
    defaults = {
        "source": airport1,
        "destination": airport2,
        "distance": 60
    }

    return Route.objects.create(**defaults)


def sample_airport(**additional) -> Airport:
    defaults = {
        "name": "Some airport",
        "closest_big_city": "London",
    }
    defaults.update(additional)

    return Airport.objects.create(**defaults)


def detail_url(airport_id: int):
    return reverse("airport:airport-detail", args=[airport_id])


class UnauthenticatedAirportTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPORT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_user(
                email="authenticated@mail.co",
                password="12R445%3df"
            )
        )

    def test_airport_list(self):
        sample_airport()
        sample_airport(name="Test airport")
        sample_airport(name="Additional airport", closest_big_city="Paris")

        response = self.client.get(AIRPORT_URL)

        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airport_detail(self):
        airport1 = sample_airport()
        airport2 = sample_airport(name="Airport 2")
        sample_route(airport1, airport2)
        sample_route(airport2, airport1)

        response = self.client.get(detail_url(airport1.id))
        serializer = AirportDetailSerializer(airport1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airport_create_forbidden(self):
        payload = {
            "name": "Forbidden",
            "closest_big_city": "None"
        }

        response = self.client.post(AIRPORT_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_superuser(
                email="admin123@mail.co",
                password="12R445%3df"
            )
        )

    def test_create(self):
        payload = {
            "name": "Truth airport",
            "closest_big_city": "USA"
        }

        response = self.client.post(AIRPORT_URL, data=payload)

        airport = Airport.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for variable_name in payload:
            self.assertEqual(
                payload[variable_name],
                getattr(airport, variable_name)
            )
