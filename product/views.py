from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import generics
# from rest_framework.filters import SearchFilter
import logging


from .filters import ProductFilter
from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer
logger = logging.getLogger(__name__)


# Create your views here.
class ProductListView(generics.ListAPIView):

    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
