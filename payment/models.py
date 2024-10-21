from django.db import models
from django.utils.translation import gettext_lazy as _

from orders.models import Order


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('initiated', 'در انتظار'),
        ('successful', 'موفق'),
        ('failed', 'خطا'),
        ('canceled', 'کنسل شده'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name='سفارش')
    authority = models.CharField(max_length=255, verbose_name='شناسه پرداخت', blank=True, null=True)
    ref_id = models.CharField(max_length=255, verbose_name='کد مرجع پرداخت', blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='initiated', verbose_name='وضعیت پرداخت')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ پرداخت')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('فاکتور')
        verbose_name_plural = _('فاکتورها')

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id} - Status: {self.status}"
