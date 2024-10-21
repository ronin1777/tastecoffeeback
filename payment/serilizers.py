from rest_framework import serializers

from orders.models import Order
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'authority',
            'ref_id',
            'status',
            'amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['authority', 'ref_id', 'created_at', 'updated_at']


class OrderPaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def validate_order_id(self, value):
        if not Order.objects.filter(id=value).exists():
            raise serializers.ValidationError("Order with the given ID does not exist.")
        return value
