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

from .models import Wish as WishModel
from .models import Psm as PsmModel
from .models import ProductPending as ProductPendingModel
from .models import Product as ProductModel
from .models import Customer as CustomerModel
from .models import Shipper as ShipperModel
from .models import Supplier as SupplierModel
from .models import Order as OrderModel
from .models import OrderHistory as OrderHistoryModel
from .models import OrderItem as OrderItemModel
from .models import OrderItem as OrderItemModel
from .models import Administrator as AdministratorModel
from .encryptor import enc_md5
from .decorators import access_decorator
from .password_checker import check_password

def guide(request):
    return render(request, 'api/guide.html')

class Order(View):
    get_method_selector = ""
    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Order, self).dispatch(request, *args, **kwargs)

    @access_decorator
    def get(self, request, **kwargs):
        token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
        if self.get_method_selector == "details":
            try:
                order_data = OrderModel.objects.get(OrderID=kwargs['orderid'])
                if token_data['usertype'] == 'customer' and str(order_data.CustomerID.CustomerID) != token_data['username']:
                    return JsonResponse({"Status": "Error", "Result": "Order is not intentioned for this CustomerID"}, status=401, safe=False)
                data = {
                    "Address": order_data.Address,
                    "OrderDateTime": order_data.OrderDateTime
                }
                order_items = OrderItemModel.objects.filter(OrderID=order_data.OrderID)
                order_item_data = []
                for item in order_items:
                    order_history = list(OrderHistoryModel.objects.filter(OrderItemID=item.OrderItemID).values())
                    order_item_data.append({
                        "ItemName": item.PsmID.ProductID.Name,
                        "ItemPicture": item.PsmID.ProductID.Picture, 
                        "ItemPrice": item.PsmID.UnitPrice,
                        "ItemQuantity": item.ItemQuantity,
                        "ShipperName": item.ShipperID.CompanyName,
                        "ShipperContact": item.ShipperID.Phone,
                        "Supplier": item.PsmID.SupplierID.CompanyName,
                        "IsCOD": item.IsCOD,
                        "ShippingStatus": item.ShippingStatus,
                        "OrderHistory": order_history
                    })
                data['ItemData'] = order_item_data
                return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
            except:
                return JsonResponse({"Status": "Error", "Result": "OrderID not found!"}, status=404, safe = False)
        elif self.get_method_selector == "list":
            if token_data['usertype'] == 'customer':
                myorder = OrderModel.objects.filter(CustomerID=token_data['username'])
                data = []
                for order in myorder:
                    {
                        data.append({
                            "OrderID": order.OrderID,
                            "OrderDateTime": order.OrderDateTime,
                        })
                    }
                print(data)
                return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Operation only allowed for customers"}, status=404, safe = False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Invalid request"}, status=404, safe = False)
    
    @access_decorator
    def post(self, request):
        data = request.body.decode('utf-8')
        data = json.loads(data)
        token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
        if token_data['usertype'] == "customer":
            try:
                my_customer = CustomerModel.objects.get(CustomerID=token_data['username'])
                my_order = OrderModel(CustomerID=my_customer, Address=data['Address'])
                my_order.save()
                if len(data['OrderItems']) > 0:
                    for item in data['OrderItems']:
                        try:
                            myproduct = ProductModel.objects.get(ProductID=item['ProductID'])
                        except:
                            my_order.delete()
                            return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)
                        try:
                            mysupplier = SupplierModel.objects.get(SupplierID=item['SupplierID'])
                        except:
                            my_order.delete()
                            return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)
                        psmid = PsmModel.objects.get(ProductID=myproduct, SupplierID=mysupplier)
                        try:
                            myitem = OrderItemModel(OrderID=my_order, PsmID=psmid, IsCOD=item['IsCOD'], ItemQuantity=item['ItemQuantity'], ShippingStatus="Pending")
                            myitem.save()
                        except:
                            my_order.delete()
                            return JsonResponse({"Status": "Error", "Result": "Invalid JSON Passed in OrderItems"}, status=404, safe=False)
                    return JsonResponse({"Status": "Success", "Result": "Order placed successfully"}, status=200, safe=False)
                else:
                    return JsonResponse({"Status": "Error", "Result": "No orderitems were passed!"}, status=404, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Invalid JSON Passed in Order"}, status=404, safe=False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Token error or Token user is not of customer type"}, status=404, safe=False)

    @access_decorator
    def delete(self, request, **kwargs):
        try:
            myorder = OrderModel.objects.get(OrderID=kwargs['orderid'])
            myorder.delete()
            return JsonResponse({"Status": "Success", "Result": "Order delete successful"}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "OrderID not found"}, status=404, safe=False)

class Supplier(View):
    post_method_selector = ""
    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Supplier, self).dispatch(request, *args, **kwargs)

    @access_decorator
    def get(self, request, supplierid):
        try:
            mysupplier = SupplierModel.objects.get(SupplierID=supplierid)
            data = serialize(mysupplier)
            del data['Password']
            return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "SupplierID not found"}, status=404, safe=False)

    @access_decorator
    def patch(self, request, supplierid):
        try:
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            if token_data['username'] == supplierid:
                mysupplier = SupplierModel.objects.filter(SupplierID=supplierid)
                data = request.body.decode('utf-8')
                data = json.loads(data)
                if mysupplier.count():
                    try:
                        try:
                            data['Password'] = enc_md5(data['Password'])
                        except:
                            pass
                        mysupplier.update(**data)
                        return JsonResponse({"Status": "Success", "Result": "Supplier updated succefully!"}, status=200, safe=False)
                    except:
                        return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed. Please check guide."}, status=404, safe=False)
                else:
                    return JsonResponse({"Status": "Success", "Result": "SupplierID not found"}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Operation on this SupplierID not allowed"}, status=401, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "Invalid SupplierID format"}, status=404, safe=False)

    @access_decorator
    def post(self, request, **kwargs):
        data = request.body.decode('utf-8')
        data = json.loads(data)
        if self.post_method_selector == "register":
            if not SupplierModel.objects.filter(Email=data['Email']).count():
                if check_password(data['Password']) == 1:
                    data['Password'] = enc_md5(data['Password'])
                    new_supplier = SupplierModel(**data)
                    new_supplier.save()
                    return JsonResponse({"Status": "Success", "Result": "New user created with Email: "+data['Email']}, status=200, safe=False)
                elif check_password(data['Password']) == 0:
                    return JsonResponse({"Status": "Error", "Result": "Weak password detected"}, status=400, safe=False)
                else:
                    return JsonResponse({"Status": "Error", "Result": "Invalid password detected"}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Supplier with same Email exists already."}, status=409, safe=False)
        elif self.post_method_selector == "login":
            try:
                mysupplier = SupplierModel.objects.get(Email=data['Email'], Password=enc_md5(data['Password']))
                token = tknzr.enc(str(mysupplier.SupplierID), mysupplier.Password[-5:], "supplier")
                return JsonResponse({"Status": "Success", "Result": "Auth Token generated successfully", "SupplierID": mysupplier.SupplierID, "Token":token}, status=200, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Invalid Email or Password!"}, status=404, safe=False)
        elif self.post_method_selector == "apply":
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            token_user = token_data['username']
            try:
                myproduct = ProductModel.objects.get(ProductID=kwargs['productid'])
            except:
                return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)
            mysupplier = SupplierModel.objects.get(SupplierID=token_user)
            try:
                if not PsmModel.objects.filter(ProductID=myproduct, SupplierID=mysupplier).count():
                    new_apply = PsmModel(ProductID=myproduct, SupplierID=mysupplier, UnitPrice=data['UnitPrice'], UnitsOnOrder=data['UnitsOnOrder'])
                    new_apply.save()
                    return JsonResponse({"Status": "Successs", "Result": 'Product: {productname} is applied by {suppliercompany} successfully'.format(productname=myproduct.Name, suppliercompany=mysupplier.CompanyName)}, status=200, safe=False)
                else:
                    return JsonResponse({"Status": "Error", "Result": "Product is already applied by Supplier"}, status=409, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed"}, status=404, safe=False)
        elif self.post_method_selector == "unapply":
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            token_user = token_data['username']
            try:
                myproduct = ProductModel.objects.get(ProductID=kwargs['productid'])
            except:
                return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)
            mysupplier = SupplierModel.objects.get(SupplierID=token_user)
            try:
                if PsmModel.objects.filter(ProductID=myproduct, SupplierID=mysupplier).count():
                    new_apply = PsmModel.objects.get(ProductID=myproduct, SupplierID=mysupplier)
                    new_apply.delete()
                    return JsonResponse({"Status": "Successs", "Result": 'Product: {productname} is unapplied by {suppliercompany} successfully'.format(productname=myproduct.Name, suppliercompany=mysupplier.CompanyName)}, status=200, safe=False)
                else:
                    return JsonResponse({"Status": "Error", "Result": "Product is already unapplied or was never applied by Supplier"}, status=409, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed"}, status=404, safe=False)
        elif self.post_method_selector == "approve":
            try:
                myorderitem = OrderItemModel.objects.get(OrderItemID=kwargs['orderitemid'])
                if myorderitem.SupplierApproved == True:
                    return JsonResponse({"Status": "Error", "Result": "OrderItem already approved by supplier"}, status=404, safe=False)
                else:
                    myorderitem.SupplierApproved=True
                    myorderitem.save()
                    return JsonResponse({"Status": "Success", "Result": "Item approved by supplier"}, status=200, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "OrderItem not found!"}, status=404, safe=False)
        elif self.post_method_selector == "reject":
            try:
                myorderitem = OrderItemModel.objects.get(OrderItemID=kwargs['orderitemid'])
                if myorderitem.SupplierApproved == True:
                    return JsonResponse({"Status": "Error", "Result": "OrderItem already approved by supplier"}, status=404, safe=False)
                else:
                    myorderitem.Cancelled=True
                    myorderitem.save()
                    # SEND EMAIL
                    return JsonResponse({"Status": "Success", "Result": "Item rejected by supplier"}, status=200, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "OrderItem not found!"}, status=404, safe=False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Invalid operation requested!"}, status=404, safe=False)
    
    @access_decorator
    def delete(self, request, supplierid):
        try:
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            if token_data['username'] == supplierid:
                mysupplier = SupplierModel.objects.get(SupplierID=supplierid)
                mysupplier.delete()
                return JsonResponse({"Status": "Success", "Result": "Deleted supplier for supplierid: "+supplierid}, status=200, safe = False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Operation on this SupplierID not allowed"}, status=401, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "SupplierID not found"}, status=404, safe=False)

class Shipper(View):
    post_method_selector = ""
    get_method_selector = ""

    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Shipper, self).dispatch(request, *args, **kwargs)

    @access_decorator
    def get(self, request, **kwargs):
        if self.get_method_selector == "shipper-details":
            try:
                myshipper = ShipperModel.objects.get(ShipperID=kwargs['shipperid'])
                data = serialize(myshipper)
                del data['Password']
                return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
            except:
                return JsonResponse({"Status": "Error", "Result": "ShipperID not found"}, status=404, safe=False)
        elif self.get_method_selector == "shipment-details":
            try:
                myorderitem = OrderItemModel.objects.get(OrderItemID=kwargs['orderitemid'])
                data = {
                    "OrderItemID": myorderitem.OrderItemID,
                    "OrderWeight": myorderitem.PsmID.ProductID.UnitWeight,
                    "ShipperStatus": myorderitem.ShippingStatus,
                    "ItemName": myorderitem.PsmID.ProductID.Name,
                    "SupplierApproved": myorderitem.SupplierApproved,
                    "PickupAddress": myorderitem.PsmID.SupplierID.Address,
                    "DeliveryAddress": myorderitem.OrderID.Address,
                    "IsCOD": myorderitem.IsCOD,
                    "Price": myorderitem.PsmID.UnitPrice * myorderitem.ItemQuantity, 
                    "CustomerName": myorderitem.OrderID.CustomerID.FirstName+" "+myorderitem.OrderID.CustomerID.LastName
                }
                
                return JsonResponse({"Status": "Success", "Result": data}, status=200, safe=False)
            except:
                return JsonResponse({"Status": "Success", "Result": "Invalid OrderID"}, status=404, safe=False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Invalid operation requested!"}, status=404, safe=False)

    @access_decorator
    def patch(self, request, shipperid):
        try:
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            if token_data['username'] == shipperid:
                myshipper = ShipperModel.objects.filter(ShipperID=shipperid)
                data = request.body.decode('utf-8')
                data = json.loads(data)
                if myshipper.count():
                    try:
                        try:
                            data['Password'] = enc_md5(data['Password'])
                        except:
                            pass
                        myshipper.update(**data)
                        return JsonResponse({"Status": "Success", "Result": "Shipper updated succefully!"}, status=200, safe=False)
                    except:
                        return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed. Please check guide."}, status=404, safe=False)
                else:
                    return JsonResponse({"Status": "Success", "Result": "ShipperID not found"}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Operation on this ShipperID not allowed"}, status=401, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "Invalid ShipperID format"}, status=404, safe=False)

    @access_decorator
    def post(self, request, **kwargs):
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
        elif self.post_method_selector == "update":
            try:
                myorderitem = OrderItemModel.objects.get(OrderItemID=kwargs['orderitemid'])
                if myorderitem.SupplierApproved == False or myorderitem.Cancelled == True:
                    return JsonResponse({"Status": "Error", "Result": "Shippment not approved or is cancelled by supplier"}, status=404, safe=False)
                else:
                    myorderitem.ShippingStatus = data['NextStatus']
                    myorderitem.save()
                    new_history = OrderHistoryModel.objects.create(OrderItemID=myorderitem, ShippingStatus=data['CompletedStatus'])
                    new_history.save()
                    return JsonResponse({"Status": "Success", "Result": "Shipping status updated to "+data['NextStatus']}, status=200, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Shippment not found"}, status=404, safe=False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Invalid operation requested!"}, status=404, safe=False)
    
    @access_decorator
    def delete(self, request, shipperid):
        try:
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            if token_data['username'] == shipperid:
                myshipper = ShipperModel.objects.get(ShipperID=shipperid)
                myshipper.delete()
                return JsonResponse({"Status": "Success", "Result": "Deleted shipper for shipperid: "+shipperid}, status=200, safe = False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Operation on this ShipperID not allowed"}, status=401, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "ShipperID not found"}, status=404, safe=False)

class Administrator(View):
    post_method_selector = ""

    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Administrator, self).dispatch(request, *args, **kwargs)

    @access_decorator
    def get(self, request, **kwargs):
        pending_products = ProductPendingModel.objects.all()
        data = []
        for product in pending_products:
            data.append({
                "ProductID": product.ProductID.ProductID,
                "Name": product.ProductID.Name,
                "Supplier Company": product.SupplierID.CompanyName,
                "Supplier Email": product.SupplierID.Email
            })
        return JsonResponse({"Status": "Success", "Result": data}, status=200, safe=False)

    @access_decorator
    def post(self, request, **kwargs):
        data = request.body.decode('utf-8')
        data = json.loads(data)
        if self.post_method_selector == "register":
            if not AdministratorModel.objects.filter(Email=data['Email']).count():
                if check_password(data['Password']) == 1:
                    data['Password'] = enc_md5(data['Password'])
                    new_administrator = AdministratorModel(**data)
                    new_administrator.save()
                    return JsonResponse({"Status": "Success", "Result": "New user created with Email: "+data['Email']}, status=200, safe=False)
                elif check_password(data['Password']) == 0:
                    return JsonResponse({"Status": "Error", "Result": "Weak password detected"}, status=400, safe=False)
                else:
                    return JsonResponse({"Status": "Error", "Result": "Invalid password detected"}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Administrator with same Email exists already."}, status=409, safe=False)
        elif self.post_method_selector == "login":
            try:
                myadministrator = AdministratorModel.objects.get(Email=data['Email'], Password=enc_md5(data['Password']))
                if myadministrator.IsApproved:
                    token = tknzr.enc(str(myadministrator.AdministratorID), myadministrator.Password[-5:], "administrator")
                    return JsonResponse({"Status": "Success", "Result": "Auth Token generated successfully", "AdministratorID": myadministrator.AdministratorID, "Token":token}, status=200, safe=False)
                else:
                    return JsonResponse({"Status": "Error", "Result": "Administrator not verified"}, status=401, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Invalid Email or Password!"}, status=404, safe=False)
        elif self.post_method_selector == "approve":
            try:
                myproductpending = ProductPendingModel.objects.get(ProductID=kwargs['productid'])
                myproductpending.delete()
                # EMAIL NOTIFICATION PENDING
                return JsonResponse({"Status": "Success", "Result": "Product approved successfully"}, status=200, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Product dosen't exist or already processed!"}, status=404, safe=False)
        elif self.post_method_selector == "reject":
            try:
                myproductpending = ProductPendingModel.objects.get(ProductID=kwargs['productid'])
                myproduct = ProductModel.objects.get(ProductID=kwargs['productid'])
                myproduct.delete()
                myproductpending.delete()
                # EMAIL NOTIFICATION PENDING
                return JsonResponse({"Status": "Success", "Result": "Product rejected successfully"}, status=200, safe=False)
            except:
                return JsonResponse({"Status": "Error", "Result": "Product dosen't exist or already processed!"}, status=404, safe=False)
        else:
            return JsonResponse({"Status": "Error", "Result": "Invalid operation requested!"}, status=404, safe=False)

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
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            if token_data['username'] == customerid:
                mycustomer = CustomerModel.objects.filter(CustomerID=customerid)
                data = request.body.decode('utf-8')
                data = json.loads(data)
                if mycustomer.count():
                    try:
                        try:
                            data['Password'] = enc_md5(data['Password'])
                        except:
                            pass
                        mycustomer.update(**data)
                        return JsonResponse({"Status": "Success", "Result": "Customer updated succefully!"}, status=200, safe=False)
                    except:
                        return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed. Please check guide."}, status=404, safe=False)
                else:
                    return JsonResponse({"Status": "Success", "Result": "CustomerID not found"}, status=404, safe=False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Operation on this CustomerID not allowed"}, status=401, safe=False)
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
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            if token_data['username'] == customerid:
                mycustomer = CustomerModel.objects.get(CustomerID=customerid)
                mycustomer.delete()
                return JsonResponse({"Status": "Success", "Result": "Deleted customer for customerid: "+customerid}, status=200, safe = False)
            else:
                return JsonResponse({"Status": "Error", "Result": "Operation on this CustomerID not allowed"}, status=401, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "CustomerID not found"}, status=404, safe=False)

class Wish(View):
    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Wish, self).dispatch(request, *args, **kwargs)

    @access_decorator
    def get(self, request):
        token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
        token_user = token_data['username']
        wishlist = WishModel.objects.filter(CustomerID=token_user)
        data = []
        for element in wishlist:
            data.append({
                "WishID": element.WishID,
                "ProductName": element.ProductID.Name,
                "ProductID": element.ProductID.ProductID, 
                "Picture": element.ProductID.Picture
                })
        return JsonResponse({"Status": "Success", "Result": data}, status=200, safe=False)

    @access_decorator
    def delete(self, request, wishid):
        try:
            mywish = WishModel.objects.get(WishID=wishid)
            mywish.delete()
            return JsonResponse({"Status": "Success", "Result": "Deleted wish for wishid: "+wishid}, status=200, safe = False)
        except:
            return JsonResponse({"Status": "Error", "Result": "WishID not found"}, status=404, safe=False)

    @access_decorator
    def post(self, request):
        try:
            data = request.body.decode('utf-8')
            data = json.loads(data)
            myproduct = ProductModel.objects.get(ProductID=data['ProductID'])
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            token_user = token_data['username']
            mycustomer = CustomerModel.objects.get(CustomerID=token_user)
            mywish = WishModel.objects.create(CustomerID=mycustomer, ProductID=myproduct)
            mywish.save()
            return JsonResponse({"Status": "Success", "Result": "Product added to Wish List."}, status=200, safe=False)
        except :
            return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed or ProductID doesn't exist."}, status=404, safe=False)

class Product(View):
    get_method_selector = ""
    #JUST TO EXEMPT CSRF VERIFICATION
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Product, self).dispatch(request, *args, **kwargs)

    @access_decorator
    def get(self, request, **kwargs):
        token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
        token_user = token_data['usertype']
        if self.get_method_selector=="details":
            try:
                myproduct = ProductModel.objects.get(ProductID=kwargs['productid'])
                if not ProductPendingModel.objects.filter(ProductID=myproduct.ProductID).count() or token_user=="administrator":
                    data = serialize(myproduct)
                    supplier_list = PsmModel.objects.filter(ProductID=myproduct.ProductID).order_by('-UnitPrice')
                    supplier_data =[]
                    for supplier_element in supplier_list:
                        supplier_data.append({
                            "SupplierID": supplier_element.SupplierID.SupplierID,
                            "SupplierCompany": supplier_element.SupplierID.CompanyName,
                            "UnitPrice": supplier_element.UnitPrice,
                            "UnitsOnOrder" :supplier_element.UnitsOnOrder
                        })
                    data['SupplierData'] = supplier_data
                    return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
                else:
                    return JsonResponse({"Status": "Error", "Result": "Product unverified by administrator"}, status=403, safe = False)
            except:
                return JsonResponse({"Status": "Error", "Result": "ProductID not found"}, status=404, safe=False)
        elif self.get_method_selector=="search":
            try:
                products = ProductModel.objects.filter(Name__icontains = kwargs['query'])
                if not list(products):
                    return JsonResponse({"Status": "Success", "Result": "No matching results found!"}, status=200, safe = False)
                else:
                    data = []
                    for product in products:
                        if not ProductPendingModel.objects.filter(ProductID=product.ProductID).count() or token_user=="administrator":
                            data.append({
                                "ProductID": product.ProductID,
                                "Name": product.Name,
                                "Picture": product.Picture
                            })
                    
                    return JsonResponse({"Status": "Success", "Result": data}, status=200, safe = False)
            except:
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
                token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
                token_user = token_data['username']
                new_product = ProductModel(**data)
                new_product.save()
                if token_data['usertype'] != "administrator":
                    mysupplier = SupplierModel.objects.get(SupplierID=token_user)
                    new_pending = ProductPendingModel.objects.create(ProductID=new_product, SupplierID=mysupplier)
                    new_pending.save()
                    return JsonResponse({"Status": "Success", "Result": "New product created named: "+data['Name']+" and is waiting to be verified by administrators."}, status=200, safe=False)
                else:
                    return JsonResponse({"Status": "Success", "Result": "New product created named: "+data['Name']}, status=200, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "Invalid JSON passed. Please check guide."}, status=404, safe=False)