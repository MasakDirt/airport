from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Order, Flight, Ticket
from airport.serializers import OrderListSerializer, OrderDetailSerializer
from airport.tests import test_flight_api
from airport.tests.test_airplane_api import sample_airplane
from airport.tests.test_airplane_type_api import sample_airplane_type
from airport.tests.test_airport_api import sample_airport, sample_route
from airport.tests.test_crew_api import sample_crew


ORDER_URL = reverse("airport:order-list")
COUNTER = 0


def sample_flight() -> Flight:
    global COUNTER

    airport1 = sample_airport()
    airport2 = sample_airport(name=f"Airport #${COUNTER}")
    route1 = sample_route(airport1, airport2)

    airplane_type = sample_airplane_type(name=f"Airplane type {COUNTER}")
    airplane1 = sample_airplane(airplane_type=airplane_type)

    maks = sample_crew(first_name="Maks")
    user = sample_crew(first_name="User")

    flight = test_flight_api.sample_flight(route=route1, airplane=airplane1)

    flight.crew.add(maks, user)

    COUNTER += 1
    return flight


def sample_ticket(**additional) -> Ticket:
    defaults = {
        "row": 1,
        "seat": 2,
        "flight": sample_flight(),
    }
    defaults.update(additional)

    return Ticket.objects.create(**defaults)


def sample_order(user: settings.AUTH_USER_MODEL) -> Order:
    defaults = {
        "user": user,
    }

    return Order.objects.create(**defaults)


def detail_url(order_id) -> str:
    return reverse("airport:order-detail", args=[order_id])


class UnauthenticatedOrderTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ORDER_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="crew@mail.co",
            password="12R445%3df"
        )
        self.client.force_authenticate(self.user)

    def test_order_list(self):
        order = sample_order(self.user)
        order2 = sample_order(self.user)
        order3 = sample_order(self.user)
        sample_ticket(order=order)
        sample_ticket(seat=1, order=order)
        sample_ticket(seat=1, row=2, order=order2)
        sample_ticket(seat=3, order=order2)
        sample_ticket(seat=1, row=3, order=order3)

        response = self.client.get(ORDER_URL)

        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_order_detail(self):
        order = sample_order(self.user)
        sample_ticket(order=order)
        sample_ticket(seat=1, order=order)
        sample_ticket(seat=1, row=2, order=order)

        response = self.client.get(detail_url(order.id))
        serializer = OrderDetailSerializer(order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_order_create(self):
        flight = sample_flight()
        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 3,
                    "flight": flight.id
                },
                {
                    "row": 1,
                    "seat": 2,
                    "flight": flight.id
                },
                {
                    "row": 1,
                    "seat": 1,
                    "flight": flight.id
                }
            ]
        }

        response = self.client.post(ORDER_URL, data=payload, format="json")
        order = Order.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order.user, self.user)
        self.assertEqual(len(order.tickets.all()), len(payload["tickets"]))
        tickets = [
            {
                "row": ticket.row,
                "seat": ticket.seat,
                "flight": ticket.flight.id
            }
            for ticket in order.tickets.all()
        ]
        for ticket in tickets:
            self.assertIn(ticket, payload["tickets"])

    def test_create_order_invalid_seat(self):
        flight = sample_flight()
        payload = {
            "tickets": [
                {
                    "row": 2,
                    "seat": 30000,
                    "flight": flight.id
                }
            ]
        }

        response = self.client.post(ORDER_URL, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            f"seat must be in range: "
            f"(1, seats_in_row)(1, {flight.airplane.seats_in_row})",
            response.data["tickets"][0]["seat"]
        )

    def test_update_not_allowed(self):
        order = sample_order(self.user)
        ticket = sample_ticket(order=order)
        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 3,
                    "flight": ticket.flight.id
                },
            ]
        }

        response = self.client.put(
            detail_url(order.id),
            data=payload,
            format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_not_allowed(self):
        order = sample_order(self.user)

        response = self.client.delete(detail_url(order.id))

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
