from django.urls import path
from .views import CartDetailView, CartItemCreateView, CartItemUpdateView, CartItemDeleteView, \
    AssignCartToUserView, OrderListView, OrderCreateView, OrderDetailView, OrderUpdateView, ShippingMethodList

app_name = 'orders'

urlpatterns = [
    # path('create-cart/', CartCreateView.as_view(), name='create-cart'),
    path('cart/<uuid:pk>/', CartDetailView.as_view(), name='retrieve-cart'),
    path('cart/', CartDetailView.as_view(), name='retrieve-cart'),  # برای کاربر احراز هویت شده

    path('add-to-cart/', CartItemCreateView.as_view(), name='create-cart-item'),


    path('update-cart/<int:product_id>/', CartItemUpdateView.as_view(), name='update-cart-item-authenticated'),  # برای کاربرانی که وارد شده‌اند
    path('update-cart/<uuid:cart_id>/<int:product_id>/', CartItemUpdateView.as_view(), name='update-cart-item-guest'),# برای مهمانان

    path('delete-cart/<int:product_id>/', CartItemDeleteView.as_view(), name='delete-cart-item-authenticated'),
    path('delete-cart/<uuid:cart_id>/<int:product_id>/', CartItemDeleteView.as_view(), name='delete-cart-item-guest'),

    path('assign-cart/', AssignCartToUserView.as_view(), name='assign-cart'),

    # orders

    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders-create/', OrderCreateView.as_view(), name='order-create'),
    path('orders-update/<int:pk>/', OrderUpdateView.as_view(), name='order-update'),
    path('orders-detail/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('shipping-methods/', ShippingMethodList.as_view(), name='shipping-method-list'),

]

