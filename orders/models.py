from django.core.validators import MinValueValidator
from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from product.models import Product

from user.models import User


class Cart(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('سبد خرید')
        verbose_name_plural = _('سبدهای خرید')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [('cart', 'product')]
        verbose_name = _('ایتم سبد خرید')
        verbose_name_plural = _('ایتم های سبد خرید')


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('shipped', 'پرداخت شده'),
        ('delivered', 'تحویل داده شده'),
        ('canceled', 'کنسل شده'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'کارت'),
        ('cod', 'نقدر در محل'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_('کاربر'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('وضعیت'))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='credit_card', null=True, blank=True, verbose_name=_('روش پرداخت'))
    shipping_address = models.TextField(verbose_name=_('ادرس تحویل'))
    shipping_method = models.ForeignKey('ShippingMethod', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='روش ارسال')
    postal_code = models.CharField(max_length=20, verbose_name=_('کد پستی'), null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('قیمت کل'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def final_price(self):
        if self.shipping_method:
            return self.total_price + self.shipping_method.price
        return self.total_price

    def complete_order(self):

        self.status = 'shipped'
        self.save()

        for item in self.items.all():
            item.product.decrease_stock(item.quantity)

    @property
    def shipping_method_name(self):
        if self.shipping_method:
            return self.shipping_method.name

    class Meta:
        verbose_name = _('سفارش')
        verbose_name_plural = _('سفارش ها')

    def __str__(self):
        return f"Order {self.id} for {self.user.name} - Status: {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=11, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    class Meta:
        verbose_name = _('ایتم سفارش')
        verbose_name_plural = _('ایتم های سفارش')


class ShippingMethod(models.Model):
    name = models.CharField(max_length=255, verbose_name='روش ارسال')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='هزینه ارسال')

    class Meta:
        verbose_name = _('روش ارسال')
        verbose_name_plural = _('روش های ارسال')

    def __str__(self):
        return self.name
