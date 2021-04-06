from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views import View

import requests
import hashlib
import json
import jwt

import api.tokenizer as tknzr

from .serializer import serialize
from .models import Product as ProductModel

from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
def get_test(request):
    return JsonResponse({"Status": "GET CHECK SUCCESSFUL"}, status=200, safe=False)

class Product(View):
    get_method_selector = ""
    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Product, self).dispatch(request, *args, **kwargs)
    
    def get(self, request, query=None, productid=None):
        if self.get_method_selector=="details":
            try:
                myproduct = ProductModel.objects.get(ProductID=productid)
                data = serialize(myproduct)
                return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
            except:
                return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)
        elif self.get_method_selector=="search":
            try:
                data = list(ProductModel.objects.filter(Name__icontains = query).values())
                if not data:
                    return JsonResponse({"Status": "Success", "Result": "No matching results found!"}, status=200, safe = False)
                else:
                    return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
            except ZeroDivisionError:
                return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Invalid operation requested!"}, status=404, safe=False)


    def delete(self, request, productid):
        try:
            myproduct = ProductModel.objects.get(ProductID=productid)
            myproduct.delete()
            return JsonResponse({"Status": "Success", "Result": "Deleted product for productid: "+productid}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)

    def post(self, request):
        try:
            data = request.body.decode('utf-8')
            data = json.loads(data)
            if ProductModel.objects.filter(ProductID=data['ProductID']).count():
                return JsonResponse({"Status": "Error", "Result": "ProductID already exist."}, status=404, safe=False)
            else:
                print("Exists!")
            new_product = ProductModel(**data)
            new_product.save()
            return JsonResponse({"Status": "Success", "Result": "Hey, POST is done!"}, status=200, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed. Please check guide."}, status=404, safe=False)