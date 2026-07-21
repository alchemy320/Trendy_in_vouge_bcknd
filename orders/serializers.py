from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )

    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "total",
        ]

    def get_total(self, obj):
        return obj.get_total()


class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "complete",
            "transaction_id",
            "orderitems",
            "total_price",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.get_total()

    def create(self, validated_data):
        orderitems_data = validated_data.pop("orderitems")

        order = Order.objects.create(**validated_data)

        for item_data in orderitems_data:
            OrderItem.objects.create(
                order=order,
                **item_data
            )

        return order

    def update(self, instance, validated_data):
        orderitems_data = validated_data.pop("orderitems", [])

        instance.complete = validated_data.get(
            "complete",
            instance.complete
        )

        instance.transaction_id = validated_data.get(
            "transaction_id",
            instance.transaction_id
        )

        instance.save()

        # Remove old order items
        instance.orderitems.all().delete()

        # Create new order items
        for item_data in orderitems_data:
            OrderItem.objects.create(
                order=instance,
                **item_data
            )

        return instance