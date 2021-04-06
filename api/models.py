import uuid
from django.db import models

class Product(models.Model):
    ProductID = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    Name = models.CharField(max_length=50)
    Description = models.TextField()
    Category =  models.CharField(max_length=50, blank=False)
    UnitWeight  = models.FloatField()
    Picture = models.CharField(max_length=300)

    def __str__(self):
        return str(self.Name)
