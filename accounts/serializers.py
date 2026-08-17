from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from .models import User


# ==================================================
# REGISTER SERIALIZER
# ==================================================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "password",
        ]

    def create(self, validated_data):

        password = validated_data.pop(
            "password"
        )

        user = User(**validated_data)

        user.set_password(password)

        user.save()

        return user


# ==================================================
# USER / PROFILE SERIALIZER
# ==================================================

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "is_staff",
            "is_superuser",
        ]

        read_only_fields = [
            "id",
            "is_staff",
            "is_superuser",
        ]


# ==================================================
# CHANGE PASSWORD SERIALIZER
# ==================================================

class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    def validate_current_password(
        self,
        value
    ):

        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Your current password is incorrect."
            )

        return value

    def validate(self, attrs):

        new_password = attrs.get(
            "new_password"
        )

        confirm_password = attrs.get(
            "confirm_password"
        )

        # Check passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "The new passwords do not match."
                }
            )

        # Django password validation
        try:
            validate_password(
                new_password,
                self.context["request"].user
            )
        except serializers.ValidationError as error:
            raise serializers.ValidationError(
                {
                    "new_password": error.messages
                }
            )

        return attrs