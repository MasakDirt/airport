from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer


AIRPLANE_TYPE_LIST_URL = reverse("airport:airplane-type-list")


def sample_airplane_type(**additional) -> AirplaneType:
    defaults = {
        "name": "Airplane"
    }
    defaults.update(additional)

    return AirplaneType.objects.create(**defaults)


class UnauthenticatedAirplaneTypeTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPLANE_TYPE_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_user(
                email="user@mail.co",
                password="pass"
            )
        )

    def test_airplane_types_list(self):
        sample_airplane_type()
        sample_airplane_type(name="new")
        sample_airplane_type(name="test")
        response = self.client.get(AIRPLANE_TYPE_LIST_URL)

        types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_type_create_user_forbidden(self):
        response = self.client.post(AIRPLANE_TYPE_LIST_URL, {"name": "FF"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_superuser(
                email="user@mail.co",
                password="pass"
            )
        )

    def test_airplane_type_create(self):
        name = "Created"
        response = self.client.post(AIRPLANE_TYPE_LIST_URL, {"name": name})

        airplane_type = AirplaneType.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], airplane_type.name)
