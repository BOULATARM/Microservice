from django.db import models

import uuid
from django.db import models
from django.utils import timezone


def generate_uuid():
    return str(uuid.uuid4())


def current_timestamp():
    return timezone.now().isoformat()


class Shipment(models.Model):

    class Status(models.TextChoices):
        PREPARING = "PREPARING"
        SHIPPED = "SHIPPED"
        IN_TRANSIT = "IN_TRANSIT"
        DELIVERED = "DELIVERED"
        CANCELLED = "CANCELLED"

    id = models.TextField(
        primary_key=True,
        default=generate_uuid,
        editable=False
    )

    order_id = models.TextField(unique=True)

    recipient_name = models.TextField()

    address = models.TextField()

    city = models.TextField()

    tracking_number = models.TextField(unique=True)

    status = models.TextField(
        choices=Status.choices,
        default=Status.PREPARING
    )

    created_at = models.TextField(
        default=current_timestamp,
        editable=False
    )

    updated_at = models.TextField(
        default=current_timestamp
    )

    class Meta:
        db_table = "shipments"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "PREPARING",
                        "SHIPPED",
                        "IN_TRANSIT",
                        "DELIVERED",
                        "CANCELLED"
                    ]
                ),
                name="shipments_status_allowed"
            )
        ]

    def __str__(self):
        return f"{self.order_id} - {self.status}"
