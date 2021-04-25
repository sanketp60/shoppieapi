import uuid
from django.db import models
import random
from django.utils import timezone

class Administrator(models.Model):
    AdministratorID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Name = models.CharField(max_length=50) #
    Email = models.EmailField(max_length=254, unique=True, blank=False) #
    Password = models.CharField(max_length=100, blank=False) #
    IsApproved = models.BooleanField(default=False) #

class Product(models.Model):
    ProductID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Name = models.CharField(max_length=50) #
    Description = models.TextField() #
    Category =  models.CharField(max_length=50, blank=False) #
    UnitWeight  = models.FloatField() #
    Picture = models.CharField(max_length=300) #

    def __str__(self):
        return "{name} [{productid}]".format(name=self.Name, productid=self.ProductID)

class Customer(models.Model):
    CustomerID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Email = models.EmailField(max_length=254, unique=True, blank=False) #
    Password = models.CharField(max_length=100, blank=False) #
    FirstName = models.CharField(max_length=40) #
    LastName = models.CharField(max_length=40) #
    DateRegistered = models.DateField(editable=False, default=timezone.now)
    Phone = models.CharField(max_length=15) #
    Address = models.TextField() #

    def __str__(self):
        return "{firstname} {lastname} - {email} [{customerid}]".format(firstname=self.FirstName, lastname=self.LastName, email=self.Email, customerid = self.CustomerID)

class Shipper(models.Model):
    ShipperID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Email = models.EmailField(max_length=254, unique=True, blank=False) #
    Password = models.CharField(max_length=100, blank=False) #
    CompanyName = models.CharField(max_length=60) #
    Phone = models.CharField(max_length=15) #

    @classmethod
    def get_random_shipper(cls):
        shppr = cls.objects.all()
        shppr_index= random.randint(0,len(shppr)-1)
        return shppr[shppr_index].pk

    def __str__(self):
        return "{companyname} - {email} [{shipperid}]".format(companyname=self.CompanyName, email=self.Email, shipperid = self.ShipperID)

class Supplier(models.Model):
    SupplierID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Email = models.EmailField(max_length=254, unique=True, blank=False) #
    Password = models.CharField(max_length=100, blank=False) #
    Address = models.TextField() #
    Phone = models.CharField(max_length=15) #
    DateRegistered = models.DateField(editable=False, default=timezone.now) #
    ContactTitle = models.CharField(max_length=40) #
    CompanyName = models.CharField(max_length=60) #

    def __str__(self):
        return "{companyname} - {email} [{supplierid}]".format(companyname=self.CompanyName, email=self.Email, supplierid = self.SupplierID)

class Wish(models.Model):
    WishID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) #
    CustomerID = models.ForeignKey(Customer, on_delete=models.CASCADE) #
    ProductID = models.ForeignKey(Product, on_delete=models.CASCADE) #

class ProductPending(models.Model):
    ProductID = models.OneToOneField(Product, primary_key=True, on_delete=models.CASCADE) #
    SupplierID = models.ForeignKey(Supplier, on_delete=models.CASCADE) #

class Psm(models.Model):
    PsmID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ProductID = models.ForeignKey(Product, on_delete=models.CASCADE) #
    SupplierID = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    UnitPrice = models.FloatField() #
    UnitsOnOrder = models.IntegerField() #

    def __str__(self):
        return self.ProductID.Name+" - "+self.SupplierID.CompanyName

class Order(models.Model):
    OrderID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CustomerID = models.ForeignKey(Customer, on_delete=models.CASCADE) #
    OrderDateTime = models.DateTimeField(default=timezone.now, editable=False)
    Address = models.TextField() #


class OrderItem(models.Model):
    OrderItemID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    OrderID = models.ForeignKey(Order, on_delete=models.CASCADE) #
    SupplierApproved = models.BooleanField(default=False) 
    Cancelled = models.BooleanField(default=False)
    PsmID = models.ForeignKey(Psm, on_delete=models.CASCADE) #
    ShipperID = models.ForeignKey(Shipper, on_delete=models.CASCADE,  default=Shipper.get_random_shipper) # RANDOM SHIPPER ASSIGN
    ShippingStatus = models.CharField(max_length=40) #
    IsCOD = models.BooleanField(default=False, editable=False)
    ItemQuantity = models.IntegerField() #

class OrderHistory(models.Model):
    OrderHistoryID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    OrderItemID = models.ForeignKey(OrderItem, on_delete=models.CASCADE) #
    ShippingStatus = models.CharField(max_length=40) #
    StatusDateTime = models.DateTimeField(default=timezone.now, editable=False)
