from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Crew
from airport.serializers import CrewSerializer


CREW_URL = reverse("airport:crew-list")


def sample_crew(**additional) -> Crew:
    defaults = {
        "first_name": "Test",
        "last_name": "Test last",
    }
    defaults.update(additional)

    return Crew.objects.create(**defaults)


class UnauthenticatedCrewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(CREW_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_user(
                email="crew@mail.co",
                password="12R445%3df"
            )
        )

    def test_crew_list(self):
        sample_crew()
        sample_crew(first_name="Maks")

        response = self.client.get(CREW_URL)

        crew = Crew.objects.all()
        serializer = CrewSerializer(crew, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_crew_create_forbidden(self):
        payload = {
            "first_name": "Forbidden",
            "last_name": "Test forbidden",
        }

        response = self.client.post(CREW_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_superuser(
                email="crew_admin@mail.co",
                password="osa2@wsadf"
            )
        )

    def test_create_crew(self):
        payload = {
            "first_name": "Maksym",
            "last_name": "Korniev",
        }

        response = self.client.post(CREW_URL, data=payload)

        crew = Crew.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for variable_name in payload:
            self.assertEqual(
                payload[variable_name],
                getattr(crew, variable_name)
            )
