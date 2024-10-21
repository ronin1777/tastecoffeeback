# from decimal import Decimal
#
# from product.models import Product
#
# CART_SESSION_ID = 'cart'
#
#
# class Cart:
#     def __init__(self, request):
#         self.session = request.session
#         cart = self.session.get(CART_SESSION_ID)
#         if not cart:
#             cart = self.session[CART_SESSION_ID] = {}
#         self.cart = cart
#
#     def __iter__(self):
#         product_ids = self.cart.keys()
#         products = Product.objects.filter(id__in=product_ids)
#         cart = self.cart.copy()
#
#         for product in products:
#             product_id = str(product.id)
#             cart_item = cart[product_id]
#             cart_item['product'] = self.serialize_product(product)  # Serialize product instance
#
#         for item in cart.values():
#             item['total_price'] = Decimal(item['price']) * item['quantity']
#             yield item
#
#     def serialize_product(self, product):
#         """Convert Product instance to a dictionary."""
#         return {
#             'id': product.id,
#
#         }
#
#     def __len__(self):
#         return sum(item['quantity'] for item in self.cart.values())
#
#     def add(self, product, quantity):
#         product_id = str(product.id)
#         if product_id not in self.cart:
#             self.cart[product_id] = {'quantity': 0, 'price': str(product.base_price)}
#         self.cart[product_id]['quantity'] += quantity
#         self.save()
#
#     def remove(self, product):
#         product_id = str(product.id)
#         if product_id in self.cart:
#             del self.cart[product_id]
#             self.save()
#
#     def save(self):
#         self.session.modified = True
#
#     def get_total_price(self):
#         return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
#
#     def clear(self):
#         del self.session[CART_SESSION_ID]
#         self.save()
