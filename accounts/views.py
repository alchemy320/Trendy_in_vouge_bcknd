from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)


# ==================================================
# REGISTER
# ==================================================

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# ==================================================
# PROFILE
# GET + PATCH
# ==================================================

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ==================================================
# CHANGE PASSWORD
# ==================================================

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={
                "request": request
            },
        )

        serializer.is_valid(raise_exception=True)

        user = request.user

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save()

        return Response(
            {
                "detail": "Password changed successfully."
            },
            status=status.HTTP_200_OK,
        )