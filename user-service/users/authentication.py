import jwt

from django.conf import settings
from rest_framework.authentication import (
    BaseAuthentication,
    get_authorization_header
)
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from .models import User


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        header = get_authorization_header(request).split()

        if not header:
            return None

        if header[0].lower() != b"bearer":
            return None

        if len(header) != 2:
            raise AuthenticationFailed(
                "Format du token invalide."
            )

        try:
            token = header[1].decode("utf-8")

            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"require": ["sub", "exp", "iat"]}
            )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed(
                "Token expiré."
            )

        except (jwt.InvalidTokenError, UnicodeDecodeError):
            raise AuthenticationFailed(
                "Token invalide."
            )

        user = User.objects.filter(
            id=payload["sub"]
        ).first()

        if user is None:
            raise AuthenticationFailed(
                "Utilisateur introuvable."
            )

        return (user, payload)

    def authenticate_header(self, request):
        return "Bearer"


class IsCustomUserAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return isinstance(request.user, User)