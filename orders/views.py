from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from .models import Cart, CartItem, Order, ShippingMethod, OrderItem
from .permissions import IsOwnerOfOrder
from .serializers import (CartSerializer, CartItemUpdateSerializer, OrderSerializer, OrdersSerializer,
                          OrderUpdateSerializer, ShippingMethodSerializer)
import uuid


from product.models import Product, ProductWeight
from user.utils import send_order_notification

class CartItemCreateView(APIView):
    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        product_id = request.data.get('product_id')
        weight_id = request.data.get('weight_id')
        quantity = int(request.data.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        weight = get_object_or_404(ProductWeight, id=weight_id)

        # دریافت UUID از فرانت‌اند برای کاربر مهمان
        cart_uuid = request.data.get('cart_uuid')

        if user:  # کاربر احراز هویت شده
            cart, created = Cart.objects.get_or_create(user=user)
        else:  # کاربر مهمان
            if cart_uuid:
                try:
                    cart = Cart.objects.get(id=uuid.UUID(cart_uuid), user__isnull=True)  # بازیابی سبد خرید مهمان
                except Cart.DoesNotExist:
                    cart = Cart.objects.create()  # اگر سبد خرید مهمان وجود نداشت، ایجاد یک سبد جدید
            else:
                cart = Cart.objects.create()  # ایجاد سبد خرید جدید اگر UUID ارسال نشده بود

        # چک کردن محصول در سبد خرید
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            cart_item.quantity += quantity  # اگر محصول در سبد خرید بود، مقدار آن افزایش پیدا کند
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class AssignCartToUserView(APIView):
    def post(self, request):
        user = request.user  # کاربر احراز هویت شده

        # دریافت UUID سبد خرید از بدنه درخواست
        cart_uuid = request.data.get('cart_uuid')
        print(f'cart_uuid: {cart_uuid}')

        if user.is_authenticated:
            # بررسی سبد خرید کاربر
            user_cart = Cart.objects.filter(user=user).first()

            if user_cart:
                # حالت اول: اگر کاربر سبد خرید داشته باشد
                if cart_uuid:
                    try:
                        guest_cart = Cart.objects.get(id=uuid.UUID(cart_uuid), user__isnull=True)
                        guest_cart.delete()  # حذف سبد خرید مهمان
                    except Cart.DoesNotExist:
                        pass  # اگر سبد خرید مهمان وجود نداشت، نیازی به کار خاصی نیست
                response = Response({'message': 'سبد خرید کاربر به روز شد.'}, status=status.HTTP_200_OK)
                response.delete_cookie('cart_uuid')  # حذف کوکی
                return response

            else:
                # حالت دوم: اگر کاربر سبد خرید ندارد ولی سبد خرید مهمان وجود دارد
                if cart_uuid:
                    try:
                        guest_cart = Cart.objects.get(id=uuid.UUID(cart_uuid), user__isnull=True)
                        # اتصال سبد خرید مهمان به کاربر
                        guest_cart.user = user
                        guest_cart.save()
                        response = Response({'message': 'سبد خرید مهمان به کاربر متصل شد.'}, status=status.HTTP_200_OK)
                        response.delete_cookie('cart_uuid')  # حذف کوکی
                        return response
                    except Cart.DoesNotExist:
                        pass  # سبد خرید مهمان وجود ندارد

                # اگر سبد خرید مهمان نیز وجود نداشت
                return Response({'message': 'کاربر بدون سبد خرید وارد شد.'}, status=status.HTTP_200_OK)

        else:
            # کاربر احراز هویت نشده
            if cart_uuid:
                try:
                    guest_cart = Cart.objects.get(id=uuid.UUID(cart_uuid), user__isnull=True)
                    response = Response({'message': 'سبد خرید مهمان وجود دارد ولی کاربر احراز هویت نشده است.'},
                                        status=status.HTTP_200_OK)
                    return response
                except Cart.DoesNotExist:
                    return Response({'message': 'سبد خرید مهمان وجود ندارد.'}, status=status.HTTP_200_OK)

            return Response({'message': 'کاربر وارد شد بدون سبد خرید.'}, status=status.HTTP_200_OK)


class CartDetailView(APIView):
    def get(self, request, *args, **kwargs):
        # گرفتن cart_id از پارامترهای query یا از URL
        cart_id = request.query_params.get('cart_id', None)
        user = request.user

        if user.is_authenticated:  # اگر کاربر احراز هویت شده است
            user_cart = Cart.objects.filter(user=user).first()
            if user_cart:
                serializer = CartSerializer(user_cart)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'کاربر بدون سبد خرید است.'}, status=status.HTTP_404_NOT_FOUND)
        elif cart_id:  # اگر کاربر مهمان باشد و cart_id وجود داشته باشد
            try:
                # چک کردن اینکه cart_id معتبر است و به یک سبد خرید مهمان تعلق دارد
                guest_cart = Cart.objects.get(id=uuid.UUID(str(cart_id)), user__isnull=True)
                serializer = CartSerializer(guest_cart)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except (Cart.DoesNotExist, ValueError) as e:
                return Response({'message': 'سبد خرید مهمان وجود ندارد.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'شناسه سبد خرید ارسال نشده است.'}, status=status.HTTP_400_BAD_REQUEST)



class CartItemUpdateView(generics.UpdateAPIView):
    serializer_class = CartItemUpdateSerializer
    lookup_field = 'product_id'

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        cart_id = self.kwargs.get('cart_id')

        if user:
            user_cart = Cart.objects.filter(user=user).first()
            if not user_cart:
                return Response({'error': 'User does not have an assigned cart.'}, status=status.HTTP_400_BAD_REQUEST)
            cart = user_cart
        else:
            cart = generics.get_object_or_404(Cart, id=cart_id, user__isnull=True)

        product_id = self.kwargs.get('product_id')
        quantity = self.request.data.get('quantity')

        cart_item = generics.get_object_or_404(CartItem, product__id=product_id, cart=cart)
        cart_item.quantity = quantity
        cart_item.save()

        response_serializer = CartItemUpdateSerializer(cart_item)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_update(serializer)


class CartItemDeleteView(APIView):
    def delete(self, request, cart_id=None, product_id=None, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None

        if user:
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                return Response({'error': 'User does not have an assigned cart.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            cart = get_object_or_404(Cart, id=cart_id, user__isnull=True)

        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

        cart_item.delete()
        return Response({'message': 'Item removed from cart successfully.'}, status=status.HTTP_204_NO_CONTENT)


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOfOrder]

    def create(self, request, *args, **kwargs):
        user = request.user

        cart_items = CartItem.objects.filter(cart__user=user)


        if not cart_items.exists():

            return Response({"error": "سبد خرید خالی است."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)


        order_id = request.data.get('id')
        if order_id and Order.objects.filter(id=order_id).exists():

            return Response({"error": "سفارش شما قبلاً ثبت شده است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.is_valid(raise_exception=True)


            # محاسبه قیمت نهایی
            total_price = 0
            for item in cart_items:
                # دسترسی به وزن و قیمت مربوط به محصول از طریق ProductWeight
                product_weight = item.product.weights.first()
                if product_weight:
                    total_price += product_weight.price * item.quantity
                else:

                    return Response({"error": "وزن محصول برای یکی از محصولات یافت نشد."}, status=status.HTTP_400_BAD_REQUEST)



            # 3. ایجاد سفارش جدید
            order = Order.objects.create(
                user=user,
                shipping_address=serializer.validated_data['shipping_address'],
                postal_code=serializer.validated_data['postal_code'],
                shipping_method=serializer.validated_data['shipping_method'],
                total_price=total_price
            )


            # 4. ایجاد آیتم‌های سفارش
            for item in cart_items:
                product_weight = item.product.weights.first()
                if product_weight:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=product_weight.price
                    )

                else:

                    return Response({"error": "وزن محصول برای یکی از محصولات یافت نشد."}, status=status.HTTP_400_BAD_REQUEST)

            user.carts.last().delete()


            order_data = OrderSerializer(order).data

            send_order_notification(order.user.name, order.user.phone_number, order.id)

            return Response(order_data, status=status.HTTP_201_CREATED)

        except Exception as e:

            return Response({"error": f"خطا در ایجاد سفارش: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class OrderUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران لاگین کرده می‌توانند سفارش را ویرایش کنند

    def get_queryset(self):
        # فقط سفارشات مربوط به کاربر جاری را برمی‌گردانیم
        user = self.request.user
        return self.queryset.filter(user=user)

    def perform_update(self, serializer):
        order = self.get_object()
        # اطمینان از این‌که کاربر صاحب سفارش است
        if order.status not in ['pending']:
            return Response({"detail": "تنها می‌توان وضعیت سفارش‌های در حال انتظار را تغییر داد."},
                            status=status.HTTP_400_BAD_REQUEST)
        if order.user != self.request.user:
            raise serializers.ValidationError("You do not have permission to edit this order.")
        serializer.save()  # اینجا خود به خود متد update از سریالایزر صدا زده می‌شود


class OrderListView(generics.ListAPIView):
    serializer_class = OrdersSerializer
    permission_classes = [IsOwnerOfOrder]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user_orders = Order.objects.filter(user=self.request.user)

        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            user_orders = user_orders.filter(status=status_filter)

        return user_orders


class OrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [IsOwnerOfOrder]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"detail": "سفارش یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        if order.status not in ['pending']:
            return Response({"detail": "تنها می‌توان وضعیت سفارش‌های در حال انتظار یا در حال پردازش را تغییر داد."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(serializer.data)


class ShippingMethodList(APIView):
    def get(self, request):
        shipping_methods = ShippingMethod.objects.all()
        serializer = ShippingMethodSerializer(shipping_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)