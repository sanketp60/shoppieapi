from django.urls import path
from .views import *

guide_urlpatterns = [
    # REFERENCE GUIDE
    path('guide/', guide, name='guide'),
]


administrator_urlpatterns = [
    # POST
    path('administrator-register/', Administrator.as_view(post_method_selector="register")),
    path('administrator-login/', Administrator.as_view(post_method_selector="login")),
    path('administrator-approve/<str:productid>', Administrator.as_view(post_method_selector="approve")),
    path('administrator-reject/<str:productid>', Administrator.as_view(post_method_selector="reject")),
    
    # GET
    path('administrator-pending/', Administrator.as_view()),
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

shipper_urlpatterns = [
    # POST
    path('shipper-register/', Shipper.as_view(post_method_selector="register")),
    path('shipper-login/', Shipper.as_view(post_method_selector="login")),
    path('shipment-update/<str:orderitemid>', Shipper.as_view(post_method_selector="update")),

    # GET
    path('shipper-details/<str:shipperid>', Shipper.as_view(get_method_selector="shipper-details")),
    path('shipment-details/<str:orderitemid>', Shipper.as_view(get_method_selector="shipment-details")),

    # PATCH
    path('shipper-update/<str:shipperid>', Shipper.as_view()),

    # DELETE
    path('shipper-delete/<str:shipperid>', Shipper.as_view()),
]

supplier_urlpatterns = [
    # POST
    path('supplier-register/', Supplier.as_view(post_method_selector="register")),
    path('supplier-login/', Supplier.as_view(post_method_selector="login")),
    path('supplier-apply/<str:productid>', Supplier.as_view(post_method_selector="apply")),
    path('supplier-unapply/<str:productid>', Supplier.as_view(post_method_selector="unapply")),
    path('supplier-approve/<str:orderitemid>', Supplier.as_view(post_method_selector="approve")),
    path('supplier-reject/<str:orderitemid>', Supplier.as_view(post_method_selector="reject")),

    # GET
    path('supplier-details/<str:supplierid>', Supplier.as_view()),

    # PATCH
    path('supplier-update/<str:supplierid>', Supplier.as_view()),

    # DELETE
    path('supplier-delete/<str:supplierid>', Supplier.as_view()),
]

wish_urlpatterns = [
    # POST
    path('wish-create/', Wish.as_view()),

    # GET
    path('wish-list/', Wish.as_view()),
    
    # DELETE
    path('wish-delete/<str:wishid>', Wish.as_view()),
]

order_urlpatterns = [
    # GET
    path('order-details/<str:orderid>', Order.as_view(get_method_selector="details")),
    path('order-list/', Order.as_view(get_method_selector="list")),

    # POST
    path('order-create/',Order.as_view()),

    # DELETE
    path('order-delete/<str:orderid>', Order.as_view())
]
urlpatterns = product_urlpatterns + customer_urlpatterns + shipper_urlpatterns + supplier_urlpatterns + wish_urlpatterns + guide_urlpatterns + administrator_urlpatterns + order_urlpatterns