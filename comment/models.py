from django.db import models

from django.utils.translation import gettext_lazy as _

from user.models import User

from product.models import Product


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('کاربر'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments'
                                , null=True)
    content = models.TextField(verbose_name=_('متن نظر'))
    reply = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE,
                              verbose_name=_('نظر والد'))
    approved = models.BooleanField(default=False, verbose_name=_('تایید شده'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))

    class Meta:
        verbose_name = _('نظر')
        verbose_name_plural = _('نظرات')

    def __str__(self):
        return f'Comment by {self.user.name}: {self.content[:20]}'
