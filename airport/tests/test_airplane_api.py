from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneListSerializer


AIRPLANES_URL = reverse("airport:airplane-list")
COUNTER = 0


def sample_airplane_type(**additional) -> AirplaneType:
    defaults = {
        "name": "Airplane"
    }
    defaults.update(additional)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**additional) -> Airplane:
    global COUNTER

    defaults = {
        "name": "Airplane1",
        "rows": 5,
        "seats_in_row": 12,
        "airplane_type": sample_airplane_type(name=f"Airplane type #{COUNTER}")
    }

    defaults.update(additional)
    COUNTER += 1
    return Airplane.objects.create(**defaults)


class UnauthenticatedAirplaneTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPLANES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_user(
                email="user@mail.co",
                password="pass"
            )
        )

    def test_airplane_list(self):
        sample_airplane()
        sample_airplane(name="New air", )
        sample_airplane(name="Air good", rows=8, )

        response = self.client.get(AIRPLANES_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_ordering(self):
        airplane_type = sample_airplane_type(name="New type")
        sample_airplane(airplane_type=airplane_type)
        sample_airplane(name="New air", airplane_type=airplane_type)
        sample_airplane(name="Air good", rows=8, airplane_type=airplane_type)
        ordering = "-airplane_type__name,name"

        response = self.client.get(AIRPLANES_URL, {"ordering": ordering})

        orders = (order for order in ordering.split(","))
        airplanes = Airplane.objects.order_by(*orders)
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
