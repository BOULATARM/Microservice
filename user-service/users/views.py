
import jwt

from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.hashers import check_password

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import User
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer
)
from .authentication import (
    JWTAuthentication,
    IsCustomUserAuthenticated
)


# 1. REGISTER
class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "message": "Utilisateur créé avec succès",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


# 2. LOGIN
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].strip()
        password = serializer.validated_data["password"]

        user = User.objects.filter(
            email__iexact=email
        ).first()

        if not user or not check_password(
            password, user.password_hash
        ):
            return Response(
                {
                    "message": "Email ou mot de passe incorrect"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user.id),
            "iat": now,
            "exp": now + timedelta(hours=1)
        }

        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        return Response({
            "message": "Connexion réussie",
            "token": token,
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": UserSerializer(user).data
        })


# 3. PROFILE
class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCustomUserAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# 4. LOGOUT
class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCustomUserAuthenticated]

    def post(self, request):
        return Response(
            {
                "success": True,
                "message": "Déconnexion réussie"
            },
            status=status.HTTP_200_OK
        )
