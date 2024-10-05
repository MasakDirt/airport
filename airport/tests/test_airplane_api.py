import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.db.models import ImageField
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneDetailSerializer,
)
from airport.tests.test_airplane_type_api import sample_airplane_type


AIRPLANES_URL = reverse("airport:airplane-list")
COUNTER = 0


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


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


def manage_image_url(airplane_id):
    return reverse("airport:airplane-manage-image", args=[airplane_id])


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

    def test_airplane_retrieve(self):
        airplane = sample_airplane()

        response = self.client.get(detail_url(airplane.pk))
        serializer = AirplaneDetailSerializer(airplane)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airplane_create_forbidden(self):
        payload = {
            "name": "Test",
            "rows": 2,
            "seats_in_row": 22,
            "airplane_type": sample_airplane_type(name="Test")
        }
        response = self.client.post(AIRPLANES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_superuser(
                email="user@mail.co",
                password="pass"
            )
        )

    def test_create_airplane(self):
        payload = {
            "name": "Admin",
            "rows": 20,
            "seats_in_row": 2,
            "airplane_type": sample_airplane_type(name="Admin").id
        }

        response = self.client.post(AIRPLANES_URL, data=payload)

        airplane = Airplane.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for variable_name in payload:
            if variable_name == "airplane_type":
                self.assertEqual(
                    payload[variable_name],
                    getattr(airplane, variable_name).id
                )
                continue

            self.assertEqual(
                payload[variable_name],
                getattr(airplane, variable_name)
            )


class AirplaneManageImageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_superuser(
                "admin@myproject.com", "password"
            )
        )
        self.airplane = sample_airplane()

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to movie"""
        url = manage_image_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                url,
                {"image": ntf},
                format="multipart"
            )
        self.airplane.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = manage_image_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_too_big_size(self):
        """Test uploading an image with big size"""
        url = manage_image_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10000, 10000))
            img.save(ntf, format="JPEG", quality=100)
            ntf.seek(0)
            response = self.client.post(
                url,
                {"image": ntf},
                format="multipart"
            )
        self.airplane.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "The maximus image size that can be uploaded is 1 MB",
            response.data["non_field_errors"][0]
        )
        with self.assertRaises(ValueError):
            self.airplane.image.size

    def test_post_image_to_airplane_list(self):
        url = AIRPLANES_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                url,
                {
                    "name": "Admin",
                    "rows": 20,
                    "seats_in_row": 2,
                    "airplane_type": sample_airplane_type(name="Admin").id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="Admin")
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = manage_image_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airplane_list(self):
        url = manage_image_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANES_URL)

        self.assertIn("image", res.data["results"][0].keys())

    def test_delete_image_from_airplane(self):
        """Test deleting an image from airplane"""
        url = manage_image_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            upload_response = self.client.post(
                url,
                {"image": ntf},
                format="multipart"
            )
        self.airplane.refresh_from_db()

        self.assertEqual(upload_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.airplane.image)

        delete_url = manage_image_url(self.airplane.id)
        delete_response = self.client.delete(delete_url)

        self.assertEqual(
            delete_response.status_code
            , status.HTTP_204_NO_CONTENT
        )
        self.airplane.refresh_from_db()

        with self.assertRaises(ValueError):
            self.airplane.image.size
