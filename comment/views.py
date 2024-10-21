from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer, ReplyCommentSerializer
from product.models import Product
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 3  # تعداد کامنت‌ها در هر صفحه
    page_size_query_param = 'page_size'  # این پارامتر را می‌توان از query string برای تغییر اندازه صفحه استفاده کرد
    max_page_size = 100  # حداکثر تعداد کامنت‌ها در یک صفحه


class ProductCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Comment.objects.filter(product__id=product_id, approved=True).order_by('-created_at')


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # گرفتن شناسه محصول از URL
        product_id = kwargs.get('product_id')

        # بررسی وجود محصول با شناسه داده‌شده
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'message': 'محصولی با این شناسه وجود ندارد.',
            }, status=status.HTTP_404_NOT_FOUND)

        # اعتبارسنجی کامنت
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)  # اضافه کردن محصول به کامنت
            return Response({
                'message': 'نظر شما با موفقیت ثبت شد.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'message': 'لطفاً اطلاعات معتبر را وارد کنید.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ReplyCommentView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = ReplyCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # ایجاد پاسخ و ارتباط با کامنت والد
        parent_comment = serializer.validated_data.get('reply')
        serializer.save(user=self.request.user, reply=parent_comment)
