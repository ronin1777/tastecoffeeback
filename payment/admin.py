from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'get_user', 'authority', 'ref_id', 'status', 'amount', 'created_at')
    search_fields = ('order__id', 'authority', 'status', 'order__user__phone_number', 'order__user__name')
    list_filter = ('status',)

    def get_user(self, obj):
        return obj.order.user if obj.order else None
    get_user.short_description = 'User'  # عنوان نمایش برای فیلد کاربر
