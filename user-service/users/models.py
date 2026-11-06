from django.db import models

import uuid

from django.db import models
from django.utils import timezone


def current_timestamp():
    return timezone.now().isoformat()


class User(models.Model):

    id = models.TextField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.TextField()

    email = models.TextField(unique=True)

    password_hash = models.TextField()

    role = models.TextField(
        default="CUSTOMER",
        db_default="CUSTOMER"
    )

    created_at = models.TextField(
        default=current_timestamp,
        editable=False
    )

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.name
