from django.contrib import admin
from django.utils.html import format_html
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'phone_number', 'name', 'email', 'is_active', 'is_admin', 'is_staff', 'profile_picture_thumbnail'
    )
    list_filter = ('is_active', 'is_admin', 'is_staff', 'location', 'birth_date')
    search_fields = ('phone_number', 'name', 'email')
    ordering = ('-phone_number',)  # می‌توانید به ترتیب دلخواه تغییر دهید
    list_editable = ('is_active', 'is_admin', 'is_staff')  # امکان ویرایش سریع فیلدهای خاص

    def profile_picture_thumbnail(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.profile_picture.url)
        return 'No Image'

    profile_picture_thumbnail.short_description = 'Profile Picture'

    fieldsets = (
        (None, {
            'fields': ('phone_number', 'name', 'email', 'bio', 'location', 'birth_date', 'postal_code', 'profile_picture')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_admin', 'is_staff')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # می‌توانید درخواست‌های خاصی را در اینجا مدیریت کنید
        return queryset

admin.site.register(User, UserAdmin)
