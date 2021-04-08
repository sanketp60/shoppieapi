from django.urls import path
from .views import *

product_urlpatterns = [
    path('product/', Product.as_view()),
    path('product/<str:productid>', Product.as_view()),
    path('product/update/<str:productid>', Product.as_view()),
    path('product/search/<str:query>', Product.as_view(get_method_selector="search")),
    path('product/details/<str:productid>', Product.as_view(get_method_selector="details")),
]

urlpatterns = product_urlpatterns