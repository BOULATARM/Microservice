from django.shortcuts import render

import uuid

from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Shipment, current_timestamp
from .serializers import (
    ShipmentSerializer,
    ShipmentCreateSerializer,
    ShipmentStatusSerializer
)


class ShipmentListCreateView(APIView):

    def get(self, request):
        shipments = Shipment.objects.all().order_by(
            "-created_at"
        )

        return Response(
            ShipmentSerializer(shipments, many=True).data
        )

    def post(self, request):
        serializer = ShipmentCreateSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["orderId"]
        address = serializer.validated_data["address"]

        if Shipment.objects.filter(order_id=order_id).exists():
            return Response(
                {"message": "Expédition déjà existante."},
                status=status.HTTP_409_CONFLICT
            )

        try:
            shipment = Shipment.objects.create(
                order_id=order_id,
                recipient_name=address["name"],
                address=address["address"],
                city=address["city"],
                tracking_number=(
                    "MSOA-" + uuid.uuid4().hex[:12].upper()
                ),
                status=Shipment.Status.PREPARING
            )
        except IntegrityError:
            return Response(
                {"message": "Conflit de création."},
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            ShipmentSerializer(shipment).data,
            status=status.HTTP_201_CREATED
        )


class ShipmentByOrderView(APIView):

    def get(self, request, order_id):
        shipment = Shipment.objects.filter(
            order_id=order_id
        ).first()

        if shipment is None:
            return Response(
                {"message": "Expédition introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            ShipmentSerializer(shipment).data
        )


class ShipmentStatusView(APIView):

    TRANSITIONS = {
        "PREPARING": ["SHIPPED", "CANCELLED"],
        "SHIPPED": ["IN_TRANSIT"],
        "IN_TRANSIT": ["DELIVERED"],
        "DELIVERED": [],
        "CANCELLED": []
    }

    def patch(self, request, shipment_id):
        serializer = ShipmentStatusSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        shipment = Shipment.objects.filter(
            id=shipment_id
        ).first()

        if shipment is None:
            return Response(
                {"message": "Expédition introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = serializer.validated_data["status"]

        if new_status not in self.TRANSITIONS.get(
            shipment.status, []
        ):
            return Response(
                {"message": "Transition de statut invalide."},
                status=status.HTTP_409_CONFLICT
            )

        shipment.status = new_status
        shipment.updated_at = current_timestamp()
        shipment.save(update_fields=["status", "updated_at"])

        return Response(
            ShipmentSerializer(shipment).data
        )
