from django.urls import path
from .views import *

guide_urlpatterns = [
    # REFERENCE GUIDE
    path('guide/', guide, name='guide'),
]

product_urlpatterns = [
    # POST
    path('product-create/', Product.as_view()),

    # GET
    path('product-search/<str:query>', Product.as_view(get_method_selector="search")),
    path('product-details/<str:productid>', Product.as_view(get_method_selector="details")),

    # PATCH
    path('product-update/<str:productid>', Product.as_view()),

    # DELETE
    path('product-delete/<str:productid>', Product.as_view()),
]

customer_urlpatterns = [
    # POST
    path('customer-register/', Customer.as_view(post_method_selector="register")),
    path('customer-login/', Customer.as_view(post_method_selector="login")),

    # GET
    path('customer-details/<str:customerid>', Customer.as_view()),

    # PATCH
    path('customer-update/<str:customerid>', Customer.as_view()),

    # DELETE
    path('customer-delete/<str:customerid>', Customer.as_view()),
]

supplier_urlpatterns = [
    # POST
    path('supplier-register/', Supplier.as_view(post_method_selector="register")),
    path('supplier-login/', Supplier.as_view(post_method_selector="login")),

    # GET
    path('supplier-details/<str:supplierid>', Supplier.as_view()),

    # PATCH
    path('supplier-update/<str:supplierid>', Supplier.as_view()),

    # DELETE
    path('supplier-delete/<str:supplierid>', Supplier.as_view()),
]

urlpatterns = product_urlpatterns + customer_urlpatterns + supplier_urlpatterns + guide_urlpatterns