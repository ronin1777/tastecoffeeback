from django.contrib import admin
from .models import Comment
from product.models import Product


class ReplyInline(admin.TabularInline):
    model = Comment
    extra = 1  # تعداد فرم‌های خالی که برای پاسخ‌ها نمایش داده شود
    fields = ('user', 'content', 'approved', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'content', 'approved', 'created_at', 'updated_at')
    list_filter = ('approved', 'created_at', 'user', 'product')
    search_fields = ('content', 'user__username', 'product__name')
    ordering = ('-created_at',)
    inlines = [ReplyInline]  # اضافه کردن Inline برای نمایش پاسخ‌ها

    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        """تایید کامنت‌های انتخاب شده."""
        queryset.update(approved=True)
        self.message_user(request, "کامنت‌های انتخاب شده تایید شدند.")
    approve_comments.short_description = "تایید کامنت‌های انتخاب شده"
