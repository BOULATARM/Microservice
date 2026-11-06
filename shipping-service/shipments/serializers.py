from rest_framework import serializers
from .models import Shipment


class AddressSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()


class ShipmentCreateSerializer(serializers.Serializer):
    orderId = serializers.CharField()
    address = AddressSerializer()


class ShipmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Shipment.Status.choices
    )


class ShipmentSerializer(serializers.ModelSerializer):
    orderId = serializers.CharField(
        source="order_id",
        read_only=True
    )

    trackingNumber = serializers.CharField(
        source="tracking_number",
        read_only=True
    )

    createdAt = serializers.CharField(
        source="created_at",
        read_only=True
    )

    updatedAt = serializers.CharField(
        source="updated_at",
        read_only=True
    )

    address = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            "id",
            "orderId",
            "address",
            "trackingNumber",
            "status",
            "createdAt",
            "updatedAt"
        ]

    def get_address(self, obj):
        return {
            "name": obj.recipient_name,
            "address": obj.address,
            "city": obj.city
        }