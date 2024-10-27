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

from product.models import Product


class CartItemCreateView(APIView):
    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)

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


# class AssignCartToUserView(APIView):
#     def post(self, request):
#         # چک کردن ورود کاربر
#         if not request.user.is_authenticated:
#             return Response({'error': 'User must be authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)
#
#         # استفاده از سریالایزر برای ولیدیشن داده‌های ورودی
#         serializer = AssignCartToUserSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         cart_id = serializer.validated_data['cart_uuid']
#         print(f'cart_id: {cart_id}')
#
#         try:
#             # پیدا کردن سبد خرید مهمان
#             guest_cart = Cart.objects.get(id=cart_id, user__isnull=True)
#             print(f'guest cart: {guest_cart}')
#             existing_cart = Cart.objects.filter(user=request.user).first()
#             print(f'existing cart: {existing_cart}')
#             if existing_cart:
#                 # اگر کاربر سبد خرید دارد و سبد خرید مهمان وجود ندارد
#                 if not guest_cart:
#                     return Response({'message': 'User already has a cart.'}, status=status.HTTP_409_CONFLICT)
#                 # اگر کاربر سبد خرید دارد و سبد خرید مهمان هم وجود دارد
#                 guest_cart.delete()
#                 return Response({'message': 'Guest cart deleted.'}, status=status.HTTP_200_OK)
#
#             # اگر کاربر سبد خرید ندارد و سبد خرید مهمان وجود دارد
#             guest_cart.user = request.user
#             guest_cart.save()
#             return Response({'message': 'Guest cart assigned to user.'}, status=status.HTTP_200_OK)
#
#         except Cart.DoesNotExist:
#             return Response({'error': 'Cart not found or already assigned to another user.'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             # مدیریت خطاهای عمومی‌تر
#             return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class CartCreateView(generics.CreateAPIView):
#     serializer_class = CartSerializer
#
#     def perform_create(self, serializer):
#         user = self.request.user if self.request.user.is_authenticated else None
#
#         # اگر کاربر مهمان باشد، سبد خرید موقتی ایجاد می‌شود
#         if not user:
#             cart = serializer.save(id=uuid.uuid4())
#         else:
#             serializer.save(id=uuid.uuid4(), user=user)


# class CartItemCreateView(generics.CreateAPIView):
#     serializer_class = CartItemSerializer
#
#     def perform_create(self, serializer):
#         user = self.request.user if self.request.user.is_authenticated else None
#         cart_id = self.request.data.get('cart')
#
#         if user:  # اگر کاربر وارد شده باشد
#             print(f"User is authenticated: {user}")
#             # بررسی کنید آیا کاربر یک سبد خرید دارد یا نه
#             user_cart = Cart.objects.filter(user=user).first()
#
#             if user_cart:  # اگر سبد خرید برای کاربر موجود باشد
#                 cart = user_cart
#             else:  # اگر سبد خرید برای کاربر موجود نباشد
#                 # از سبد خرید ناشناس استفاده کنید و آن را به کاربر اختصاص دهید
#                 anonymous_cart = Cart.objects.filter(id=cart_id).first()
#                 if anonymous_cart:
#                     anonymous_cart.user = user
#                     anonymous_cart.save()
#                     cart = anonymous_cart
#                 else:
#                     cart = Cart.objects.create(user=user)  # ایجاد یک سبد خرید جدید برای کاربر
#
#         else:  # اگر کاربر وارد نشده باشد
#             # استفاده از سبد خرید ناشناس
#             cart = generics.get_object_or_404(Cart, id=cart_id)
#
#         product_id = self.request.data.get('product')
#         quantity = int(self.request.data.get('quantity', 1))
#         product = generics.get_object_or_404(Product, id=product_id)
#
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             product=product,
#             defaults={'quantity': quantity}
#         )
#
#         if not created:
#             cart_item.quantity += quantity
#             cart_item.save()
#
#         response_serializer = CartItemReadSerializer(cart_item)
#         return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# class CartDetailView(generics.RetrieveAPIView):
#     serializer_class = CartSerializer
#
#     def get_object(self):
#         user = self.request.user if self.request.user.is_authenticated else None
#         cart_id = self.kwargs.get('pk')
#
#         if user:  # If the user is authenticated, fetch their cart
#             return generics.get_object_or_404(Cart, user=user)
#         else:  # Otherwise, get the cart by its ID from the URL
#             return generics.get_object_or_404(Cart, id=cart_id)
#


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

        # 1. بررسی اینکه آیا سبد خرید خالی است یا خیر
        if not cart_items.exists():
            return Response({"error": "سبد خرید خالی است."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. استفاده از serializer برای اعتبارسنجی داده‌ها
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 3. ایجاد سفارش جدید
        try:
            order = Order.objects.create(
                user=user,
                shipping_address=serializer.validated_data['shipping_address'],
                postal_code=serializer.validated_data['postal_code'],
                shipping_method=serializer.validated_data['shipping_method'],
                total_price=sum(item.product.base_price * item.quantity for item in cart_items)
            )

            # 4. ایجاد آیتم‌های سفارش
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.base_price
                )

            # 5. حذف سبد خرید کاربر
            user.carts.last().delete()

            # 6. استفاده از serializer برای بازگرداندن اطلاعات کامل سفارش
            order_data = OrderSerializer(order).data
            return Response(order_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": "خطا در ایجاد سفارش: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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