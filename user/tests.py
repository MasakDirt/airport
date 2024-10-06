from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.serializers import UserSerializer


USER_CREATE = reverse("user:user-register")
USER_DETAIL = reverse("user:user-detail")


class UnauthenticatedCreateUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        payload = {
            "email": "test@mail.com",
            "first_name": "First test",
            "last_name": "Last test",
            "password": "pas24r_#w33",
        }

        response = self.client.post(USER_CREATE, data=payload)

        user = get_user_model().objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(payload["password"], user.password)
        for variable_name in payload:
            if variable_name != "password":
                self.assertEqual(
                    payload[variable_name],
                    getattr(user, variable_name)
                )


class UnauthenticatedManageUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(USER_DETAIL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedManageUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="authenticated@mail.com",
            password="pas243wr",
            first_name="First test",
            last_name="Last test",
        )
        self.client.force_authenticate(self.user)

    def test_detail_user(self):
        response = self.client.get(USER_DETAIL)

        serializer = UserSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
