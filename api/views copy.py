from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views import View
import requests
import hashlib
import json
import jwt

import api.tokenizer as tknzr
from .serializer import serialize
from django.core import serializers

from .models import Product as ProductModel

from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
def get_test(request):
    return JsonResponse({"Status": "GET CHECK SUCCESSFUL"}, status=200, safe=False)

class Product(View):
    somevalue = ""

    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Product, self).dispatch(request, *args, **kwargs)
    
    def get(self, request, productid):
        try:
            myproduct = ProductModel.objects.get(ProductID=productid)
            data = serialize(myproduct)
            return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)

    def get(self, request, query):
        try:
            data = list(ProductModel.objects.filter(Name__icontains = query).values())
            if not data:
                return JsonResponse({"Status": "Success", "Result": "No matching results found!"}, status=200, safe = False)
            else:
                return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
        except ZeroDivisionError:
            return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)


    def delete(self, request, productid):
        try:
            myproduct = ProductModel.objects.get(ProductID=productid)
            myproduct.delete()
            return JsonResponse({"Status": "Success", "Result": "Deleted product for productid: "+productid}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)