from django import forms
from django.contrib import admin
from .models import BlogPost, Paragraph, BlogImage
from ckeditor.widgets import CKEditorWidget


class ParagraphAdminForm(forms.ModelForm):
    class Meta:
        model = Paragraph
        fields = '__all__'
        widgets = {
            'content': CKEditorWidget(config_name='default'),  # استفاده از CKEditor برای فیلد محتوا
        }


class ParagraphAdmin(admin.TabularInline):
    model = Paragraph
    form = ParagraphAdminForm
    extra = 1  # تعداد پاراگراف‌های خالی که نشان داده می‌شود


class BlogPostAdmin(admin.ModelAdmin):
    inlines = [ParagraphAdmin]


admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogImage)
