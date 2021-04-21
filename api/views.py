from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.core import serializers
from django.views import View

import requests
import json
import jwt

import api.tokenizer as tknzr

from .serializer import serialize
from .models import Product as ProductModel
from .models import Customer as CustomerModel
from .models import Shipper as ShipperModel
from .encryptor import enc_md5
from .decorators import access_decorator
from .password_checker import check_password

def guide(request):
    return render(request, 'api/guide.html')

class Shipper(View):
    post_method_selector = ""

    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Shipper, self).dispatch(request, *args, **kwargs)

    @access_decorator
    def get(self, request, shipperid):
        try:
            myshipper = ShipperModel.objects.get(ShipperID=shipperid)
            data = serialize(myshipper)
            del data['Password']
            return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "ShipperID not found"}, status=404, safe=False)

    @access_decorator
    def patch(self, request, shipperid):
        try:
            myshipper = ShipperModel.objects.filter(ShipperID=shipperid)
            data = request.body.decode('utf-8')
            data = json.loads(data)
            if myshipper.count():
                try:
                    myshipper.update(**data)
                    return JsonResponse({"Status": "Success", "Result": "Shipper updated succefully!"}, status=200, safe=False)
                except:
                    return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed. Please check guide."}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Success", "Result": "ShipperID not found"}, status=404, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "Invalid ShipperID format"}, status=404, safe=False)

    @access_decorator
    def post(self, request):
        data = request.body.decode('utf-8')
        data = json.loads(data)
        if self.post_method_selector == "register":
            if not ShipperModel.objects.filter(Email=data['Email']).count():
                if check_password(data['Password']) == 1:
                    data['Password'] = enc_md5(data['Password'])
                    new_shipper = ShipperModel(**data)
                    new_shipper.save()
                    return JsonResponse({"Status": "Success", "Result": "New user created with Email: "+data['Email']}, status=200, safe=False)
                elif check_password(data['Password']) == 0:
                    return JsonResponse({"Status": "Error", "Result": "Weak password detected"}, status=400, safe=False)
                else:
                    return JsonResponse({"Status": "Error", "Result": "Invalid password detected"}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Shipper with same Email exists already."}, status=409, safe=False)
        elif self.post_method_selector == "login":
            try:
                myshipper = ShipperModel.objects.get(Email=data['Email'], Password=enc_md5(data['Password']))
                token = tknzr.enc(str(myshipper.ShipperID), myshipper.Password[-5:], "shipper")
                return JsonResponse({"Status": "Success", "Result": "Auth Token generated successfully", "ShipperID": myshipper.ShipperID, "Token":token}, status=200, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Invalid Email or Password!"}, status=404, safe=False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Invalid operation requested!"}, status=404, safe=False)
    
    @access_decorator
    def delete(self, request, shipperid):
        try:
            myshipper = ShipperModel.objects.get(ShipperID=shipperid)
            myshipper.delete()
            return JsonResponse({"Status": "Success", "Result": "Deleted shipper for shipperid: "+shipperid}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "ShipperID not found"}, status=404, safe=False)

class Customer(View):
    post_method_selector = ""

    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Customer, self).dispatch(request, *args, **kwargs)

    @access_decorator
    def get(self, request, customerid):
        try:
            mycustomer = CustomerModel.objects.get(CustomerID=customerid)
            data = serialize(mycustomer)
            del data['Password']
            return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "CustomerID not found"}, status=404, safe=False)

    @access_decorator
    def patch(self, request, customerid):
        try:
            mycustomer = CustomerModel.objects.filter(CustomerID=customerid)
            data = request.body.decode('utf-8')
            data = json.loads(data)
            if mycustomer.count():
                try:
                    mycustomer.update(**data)
                    return JsonResponse({"Status": "Success", "Result": "Customer updated succefully!"}, status=200, safe=False)
                except:
                    return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed. Please check guide."}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Success", "Result": "CustomerID not found"}, status=404, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "Invalid CustomerID format"}, status=404, safe=False)

    @access_decorator
    def post(self, request):
        data = request.body.decode('utf-8')
        data = json.loads(data)
        if self.post_method_selector == "register":
            if not CustomerModel.objects.filter(Email=data['Email']).count():
                if check_password(data['Password']) == 1:
                    data['Password'] = enc_md5(data['Password'])
                    new_customer = CustomerModel(**data)
                    new_customer.save()
                    return JsonResponse({"Status": "Success", "Result": "New user created with Email: "+data['Email']}, status=200, safe=False)
                elif check_password(data['Password']) == 0:
                    return JsonResponse({"Status": "Error", "Result": "Weak password detected"}, status=400, safe=False)
                else:
                    return JsonResponse({"Status": "Error", "Result": "Invalid password detected"}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Customer with same Email exists already."}, status=409, safe=False)
        elif self.post_method_selector == "login":
            try:
                mycustomer = CustomerModel.objects.get(Email=data['Email'], Password=enc_md5(data['Password']))
                token = tknzr.enc(str(mycustomer.CustomerID), mycustomer.Password[-5:], "customer")
                return JsonResponse({"Status": "Success", "Result": "Auth Token generated successfully", "CustomerID": mycustomer.CustomerID, "Token":token}, status=200, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Invalid Email or Password!"}, status=404, safe=False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Invalid operation requested!"}, status=404, safe=False)
    
    @access_decorator
    def delete(self, request, customerid):
        try:
            mycustomer = CustomerModel.objects.get(CustomerID=customerid)
            mycustomer.delete()
            return JsonResponse({"Status": "Success", "Result": "Deleted customer for customerid: "+customerid}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "CustomerID not found"}, status=404, safe=False)

class Product(View):
    get_method_selector = ""
    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Product, self).dispatch(request, *args, **kwargs)

    @access_decorator
    def get(self, request, **kwargs):
        if self.get_method_selector=="details":
            try:
                myproduct = ProductModel.objects.get(ProductID=kwargs['productid'], Is_approved=True)
                data = serialize(myproduct)
                return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
            except:
                return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)
        elif self.get_method_selector=="search":
            try:
                data = list(ProductModel.objects.defer('Is_approved').filter(Name__icontains = kwargs['query'], Is_approved=True).values())
                if not data:
                    return JsonResponse({"Status": "Success", "Result": "No matching results found!"}, status=200, safe = False)
                else:
                    return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
            except ZeroDivisionError:
                return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Invalid operation requested!"}, status=404, safe=False)

    @access_decorator
    def patch(self, request, productid):
        try:
            myproduct = ProductModel.objects.filter(ProductID=productid)
            data = request.body.decode('utf-8')
            data = json.loads(data)
            if myproduct.count():
                try:
                    myproduct.update(**data)
                    return JsonResponse({"Status": "Success", "Result": "Product updated succefully!"}, status=200, safe=False)
                except:
                    return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed. Please check guide."}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Success", "Result": "ProductID not found"}, status=404, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "Invalid ProductID format"}, status=404, safe=False)

    @access_decorator
    def delete(self, request, productid):
        try:
            myproduct = ProductModel.objects.get(ProductID=productid)
            myproduct.delete()
            return JsonResponse({"Status": "Success", "Result": "Deleted product for productid: "+productid}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)

    @access_decorator
    def post(self, request):
        try:
            data = request.body.decode('utf-8')
            data = json.loads(data)
            if ProductModel.objects.filter(Name=data['Name']).count():
                return JsonResponse({"Status": "Error", "Result": "Product with same name exists already."}, status=409, safe=False)
            else:
                new_product = ProductModel(**data)
                new_product.save()
                return JsonResponse({"Status": "Success", "Result": "New product created named: "+data['Name']}, status=200, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed. Please check guide."}, status=404, safe=False)