from django.db import models

class Product(models.Model):
    ProductID = models.BigIntegerField(primary_key=True)
    Name = models.CharField(max_length=50)
    Description = models.CharField(max_length=50)
    Category =  models.CharField(max_length=50, blank=False)
    UnitWeight  = models.FloatField()
    Picture = models.CharField(max_length=300)

    def __str__(self):
        return str(self.ProductID)