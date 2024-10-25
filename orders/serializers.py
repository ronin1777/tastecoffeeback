from rest_framework import serializers

from .models import CartItem, Cart, OrderItem, Order, ShippingMethod
from tastecofee import settings


class AssignCartToUserSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField(required=True)


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']


class CartItemReadSerializer(serializers.ModelSerializer):
    total_price_items = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'total_price_items']

    def get_total_price_items(self, obj):
        return obj.product.base_price * obj.quantity

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_image(self, obj):
        return obj.product.primary_image



class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemReadSerializer(many=True, read_only=True)
    total_price_cart = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'total_price_cart', 'items']

    def get_total_price_cart(self, obj):
        return sum(item.product.base_price * item.quantity for item in obj.items.all())


class OrderSerializer(serializers.ModelSerializer):
    final_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = ['id', 'shipping_address', 'postal_code', 'shipping_method', 'final_price']  # افزودن postal_code

    def validate_shipping_address(self, value):
        if not value:
            raise serializers.ValidationError("لطفا آدرس تحویل را وارد کنید.")
        return value

    def validate_postal_code(self, value):
        if not value:
            raise serializers.ValidationError("لطفا کد پستی را وارد کنید.")
        return value

    def validate_shipping_method(self, value):
        if value is None:
            raise serializers.ValidationError("لطفا یک روش ارسال انتخاب کنید.")
        return value

    def validate_postal_code(self, value):
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("کدپستی باید دقیقاً ۱۰ رقم باشد.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = CartItem.objects.filter(cart__user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("سبد خرید خالی است.")

        # ایجاد سفارش جدید
        order = Order.objects.create(
            user=user,
            shipping_address=validated_data['shipping_address'],
            postal_code=validated_data['postal_code'],  # ذخیره کد پستی
            shipping_method=validated_data['shipping_method'],
            total_price=sum(item.product.base_price * item.quantity for item in cart_items)
        )

        # ایجاد آیتم‌های سفارش
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.base_price
            )

        user.carts.last().delete()

        return order


class OrderUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_method', 'postal_code', 'final_price', 'shipping_method_name']

    def validate_shipping_address(self, value):
        if not value:
            raise serializers.ValidationError("Shipping address cannot be empty.")
        return value

    def validate_shipping_method(self, value):
        if value is None:
            raise serializers.ValidationError("Shipping method cannot be null.")
        return value

    def validate_postal_code(self, value):
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("کدپستی باید دقیقاً ۱۰ رقم باشد.")
        return value

    def update(self, instance, validated_data):
        new_shipping_method = validated_data.get('shipping_method', instance.shipping_method)
        instance.shipping_address = validated_data.get('shipping_address', instance.shipping_address)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.shipping_method = new_shipping_method
        instance.save()

        return instance

    def calculate_total_price(self, order, new_shipping_method):
        # منطق محاسبه total_price
        # فرض کنید shipping_method دارای یک ویژگی قیمت است
        return order.total_price - (
            order.shipping_method.price if order.shipping_method else 0) + new_shipping_method.price


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    coffee_type = serializers.CharField(source='product.coffee_type', read_only=True)
    weight = serializers.CharField(source='product.weight', read_only=True)
    primary_image = serializers.CharField(source='product.primary_image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'coffee_type', 'weight', 'quantity', 'price', 'primary_image']


class OrdersSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    authority = serializers.SerializerMethodField()
    ref_id = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user_name', 'status', 'postal_code', 'payment_method',
                  'shipping_address', 'shipping_method', 'shipping_method_name',
                  'total_price', 'final_price', 'created_at', 'updated_at',
                  'items', 'authority', 'ref_id']

    def get_authority(self, obj):
        payment = obj.payments.first()
        return payment.authority if payment else None

    def get_ref_id(self, obj):
        payment = obj.payments.first()
        return payment.ref_id if payment else None


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'price']
