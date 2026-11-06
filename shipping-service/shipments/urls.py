from django.urls import path
from .views import (
    ShipmentListCreateView,
    ShipmentByOrderView,
    ShipmentStatusView
)

urlpatterns = [
    path("api/shipments", ShipmentListCreateView.as_view()),
    path(
        "api/shipments/order/<str:order_id>",
        ShipmentByOrderView.as_view()
    ),
    path(
        "api/shipments/<str:shipment_id>/status",
        ShipmentStatusView.as_view()
    ),
]