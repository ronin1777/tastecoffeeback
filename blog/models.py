from django.db import models
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('بلاگ')
        verbose_name_plural = _('بلاگ ها')

    def __str__(self):
        return self.title


class Paragraph(models.Model):
    blog_post = models.ForeignKey(BlogPost, related_name='paragraphs', on_delete=models.CASCADE)
    content = RichTextField()  # برای محتوای پاراگراف
    order = models.PositiveIntegerField(default=0)  # برای مرتب‌سازی پاراگراف‌ها

    class Meta:
        verbose_name = _('پاراگراف')
        verbose_name_plural = _('پاراگراف ها')

    class Meta:
        ordering = ['order']  # مرتب‌سازی بر اساس order


class BlogImage(models.Model):
    blog_post = models.ForeignKey(BlogPost, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_images/')  # مسیر ذخیره‌سازی تصاویر
    caption = models.CharField(max_length=200, blank=True, null=True)  # توضیحات تصویر
    order = models.PositiveIntegerField(default=0)  # برای مرتب‌سازی تصاویر


    class Meta:
        ordering = ['order']  # مرتب‌سازی بر اساس order
        verbose_name = _('عکس بلاگ')
        verbose_name_plural = _('عکس بلاگ ها')

