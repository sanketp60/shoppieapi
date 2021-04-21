import uuid
from django.db import models
from django.utils import timezone

class Product(models.Model):
    ProductID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Name = models.CharField(max_length=50)
    Description = models.TextField()
    Category =  models.CharField(max_length=50, blank=False)
    UnitWeight  = models.FloatField()
    Picture = models.CharField(max_length=300)
    Is_approved = models.BooleanField(default=False)

    def __str__(self):
        return "{name} [{productid}]".format(name=self.Name, productid=self.ProductID)

class Customer(models.Model):
    CustomerID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Email = models.EmailField(max_length=254, unique=True, blank=False)
    Password = models.CharField(max_length=100, blank=False)
    FirstName = models.CharField(max_length=40)
    LastName = models.CharField(max_length=40)
    DateRegistered = models.DateField(editable=False, default=timezone.now)
    Phone = models.CharField(max_length=15)
    Address = models.TextField()

    def __str__(self):
        return "{firstname} {lastname} - {email} [{customerid}]".format(firstname=self.FirstName, lastname=self.LastName, email=self.Email, customerid = self.CustomerID)

class Shipper(models.Model):
    ShipperID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Email = models.EmailField(max_length=254, unique=True, blank=False)
    Password = models.CharField(max_length=100, blank=False)
    CompanyName = models.CharField(max_length=60)
    Phone = models.CharField(max_length=15)

    def __str__(self):
        return "{companyname} - {email} [{shipperid}]".format(companyname=self.CompanyName, email=self.Email, shipperid = self.ShipperID)