from django.urls import include, path
from rest_framework.routers import DefaultRouter

from airport.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    RouteViewSet,
    CrewViewSet,
    FlightViewSet,
    OrderViewSet,
)


router = DefaultRouter()

router.register(
    "airplane_types",
    AirplaneTypeViewSet,
    basename="airplane-type"
)
router.register("airplanes", AirplaneViewSet, basename="airplane")
router.register("airports", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")
router.register("crew", CrewViewSet, basename="crew")
router.register("flights", FlightViewSet, basename="flight")
router.register("my_orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"
