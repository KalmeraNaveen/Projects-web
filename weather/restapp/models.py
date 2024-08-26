from django.db import models

#Create your models here.
class weathermodel(models.Model):
    url=models.URLField()
    City=models.CharField(max_length=66)
    Rain=models.CharField(max_length=5)
    Temperature=models.CharField(max_length=5)

class registermodel(models.Model):
    Username=models.CharField(max_length=20,unique=True)
    Email=models.CharField(max_length=35,unique=True)
    Password=models.CharField(max_length=35)
    City=models.TextField(null=True,blank=True)