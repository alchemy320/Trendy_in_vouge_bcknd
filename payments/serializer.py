from rest_framework import serializers

class PaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=10)
    description = serializers.CharField(max_length=255, required=False)