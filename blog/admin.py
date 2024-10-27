from django import forms
from django.contrib import admin
from .models import BlogPost, Paragraph, BlogImage
from ckeditor.widgets import CKEditorWidget


class ParagraphInline(admin.TabularInline):
    model = Paragraph
    extra = 1  # تعداد فرم‌های خالی اضافی برای افزودن پاراگراف
    fields = ('content', 'order')
    ordering = ('order',)  # مرتب‌سازی پاراگراف‌ها بر اساس `order`

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1  # تعداد فرم‌های خالی اضافی برای افزودن تصویر
    fields = ('image', 'caption', 'order')
    ordering = ('order',)  # مرتب‌سازی تصاویر بر اساس `order`

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    inlines = [ParagraphInline, BlogImageInline]  # افزودن inline‌ها برای مدل بلاگ
