from rest_framework import serializers

from .models import Comment
from datetime import datetime


class ReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

    def get_user(self, obj):
        return obj.user.name


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # نمایش نام کاربر به‌جای ID
    product = serializers.PrimaryKeyRelatedField(read_only=True)  # شناسه محصول
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at', 'approved', 'product', 'replies']

    def get_user(self, obj):
        return obj.user.name

    def get_replies(self, obj):
        # دریافت ریپلای‌ها برای کامنت والد
        replies = obj.replies.filter(approved=True)
        return ReplySerializer(replies, many=True).data  # استفاده از سریالایزر ریپلای برای نمایش داده‌ها


class CommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'product', 'content', 'reply']
        read_only_fields = ['user', 'product']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.user
        validated_data['approved'] = False
        return super().create(validated_data)


class ReplyCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'reply']  # فقط محتوای نظر و کامنت والد

    def create(self, validated_data):
        # کاربر را به عنوان نظر دهنده تعیین کنید
        validated_data['user'] = self.context['request'].user
        reply = validated_data.get('reply')

        # بررسی وجود کامنت والد
        if reply and not Comment.objects.filter(id=reply.id).exists():
            raise serializers.ValidationError("کامنت والد پیدا نشد.")

        return super().create(validated_data)
