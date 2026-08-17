from rest_framework import serializers
from orders.models import Order


class PaymentSerializer(serializers.Serializer):

    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source="order"
    )

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    phone_number = serializers.CharField(
        max_length=20
    )

    account_reference = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    description = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )

    def validate_phone_number(self, value):

        # Remove spaces, dashes and +
        value = (
            value
            .replace(" ", "")
            .replace("-", "")
            .replace("+", "")
        )

        # ==========================================
        # 07XXXXXXXX
        # 011XXXXXXXX
        # ==========================================

        if value.startswith("07") and len(value) == 10:
            value = "254" + value[1:]

        elif value.startswith("01") and len(value) == 10:
            value = "254" + value[1:]

        # ==========================================
        # 7XXXXXXXX
        # 1XXXXXXXX
        # ==========================================

        elif value.startswith("7") and len(value) == 9:
            value = "254" + value

        elif value.startswith("1") and len(value) == 9:
            value = "254" + value

        # ==========================================
        # FINAL VALIDATION
        # Accept:
        #
        # 2547XXXXXXXX
        # 2541XXXXXXXX
        # ==========================================

        if not value.startswith(("2547", "2541")) or len(value) != 12:
            raise serializers.ValidationError(
                "Enter a valid Kenyan mobile phone number."
            )

        return value