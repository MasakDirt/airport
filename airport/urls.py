from django.urls import include, path
from rest_framework.routers import DefaultRouter

from airport.views import AirplaneTypeViewSet, AirplaneViewSet


router = DefaultRouter()

router.register(
    "airplane_types",
    AirplaneTypeViewSet,
    basename="airplane_type"
)
router.register("airplanes", AirplaneViewSet, basename="airplane")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"
