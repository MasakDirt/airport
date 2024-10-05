from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Route
from airport.serializers import RouteListSerializer, RouteDetailSerializer
from airport.tests.test_airport_api import sample_airport


ROUTE_URL = reverse("airport:route-list")


def sample_route(airport1: Airport, airport2: Airport) -> Route:
    defaults = {
        "source": airport1,
        "destination": airport2,
        "distance": 60
    }

    return Route.objects.create(**defaults)


def detail_url(route_id: int):
    return reverse("airport:route-detail", args=[route_id])


class UnauthenticatedRouteTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ROUTE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_user(
                email="new_user@test.com",
                password="9wd*ksda@1"
            )
        )

    def test_route_list(self):
        airport1 = sample_airport(name="Airport 1")
        airport2 = sample_airport(name="Airport 2")
        airport3 = sample_airport(name="Airport 3")
        airport4 = sample_airport(name="Airport 4")
        sample_route(airport1, airport2)
        sample_route(airport3, airport4)
        sample_route(airport2, airport1)
        sample_route(airport4, airport3)

        response = self.client.get(ROUTE_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for route in response.data["results"]:
            self.assertIn(route, serializer.data)

    def test_route_filtering_by_source_city(self):
        airport1 = sample_airport(name="Airport 1", closest_big_city="Kiyv")
        airport2 = sample_airport(name="Airport 2")
        airport3 = sample_airport(name="Airport 3")
        airport4 = sample_airport(name="Airport 4", closest_big_city="Kiyv")
        sample_route(airport1, airport2)
        sample_route(airport3, airport4)
        sample_route(airport2, airport1)
        sample_route(airport4, airport3)

        s_city = "ki"
        response = self.client.get(ROUTE_URL, {"s_city": s_city})

        routes = Route.objects.filter(
            source__closest_big_city__icontains=s_city
        )
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_filtering_by_destination_city(self):
        airport1 = sample_airport(
            name="Airport 1",
            closest_big_city="Las Vegas"
        )
        airport2 = sample_airport(name="Airport 2", closest_big_city="LA")
        airport3 = sample_airport(name="Airport 3")
        airport4 = sample_airport(name="Airport 4", closest_big_city="Kiyv")
        sample_route(airport1, airport2)
        sample_route(airport3, airport4)
        sample_route(airport2, airport1)
        sample_route(airport4, airport3)

        d_city = "la"
        response = self.client.get(ROUTE_URL, {"d_city": d_city})

        routes = Route.objects.filter(
            destination__closest_big_city__icontains=d_city
        )
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for route in response.data["results"]:
            self.assertIn(route, serializer.data)

    def test_route_filtering_by_source_airport(self):
        airport1 = sample_airport(name="Airport LA", closest_big_city="LA")
        airport2 = sample_airport(name="Airport Las Vegas")
        airport3 = sample_airport(name="Airport Landaria")
        airport4 = sample_airport(name="Air", closest_big_city="Poland")
        sample_route(airport1, airport2)
        sample_route(airport3, airport4)
        sample_route(airport2, airport1)
        sample_route(airport4, airport3)

        s_airport = "la"
        response = self.client.get(ROUTE_URL, {"s_airport": s_airport})

        routes = Route.objects.filter(
            source__name__icontains=s_airport
        )
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for route in response.data["results"]:
            self.assertIn(route, serializer.data)

    def test_route_filtering_by_destination_airport(self):
        airport1 = sample_airport(
            name="Airport 1",
            closest_big_city="Las Vegas"
        )
        airport2 = sample_airport(name="Airport 2", closest_big_city="Madrid")
        airport3 = sample_airport(name="Airport 3")
        airport4 = sample_airport(name="Just flying 4")
        sample_route(airport1, airport2)
        sample_route(airport3, airport4)
        sample_route(airport2, airport1)
        sample_route(airport4, airport3)

        d_airport = "la"
        response = self.client.get(ROUTE_URL, {"d_airport": d_airport})

        routes = Route.objects.filter(
            destination__name__icontains=d_airport
        )
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_detail(self):
        route = sample_route(
            sample_airport(name="Air1"),
            sample_airport(name="Air2")
        )

        response = self.client.get(detail_url(route.id))
        serializer = RouteDetailSerializer(route)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_route_create_forbidden(self):
        payload = {
            "source": sample_airport(name="Air1"),
            "destination": sample_airport(name="Air2"),
            "distance": 60
        }
        response = self.client.post(ROUTE_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_superuser(
                email="adminka123@mail.co",
                password="12R445%3df"
            )
        )

    def test_create(self):
        payload = {
            "source": sample_airport(name="Air1").id,
            "destination": sample_airport(name="Air2").id,
            "distance": 60
        }

        response = self.client.post(ROUTE_URL, data=payload)

        route = Route.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for variable_name in payload:
            if variable_name == "distance":
                self.assertEqual(
                    payload[variable_name],
                    getattr(route, variable_name)
                )
                continue

            self.assertEqual(
                payload[variable_name],
                getattr(route, variable_name).id
            )
