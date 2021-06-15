from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    Owner = models.ForeignKey(User, on_delete=models.CASCADE)
    Name = models.TextField(blank=False)

class StockGroup(models.Model):
    Owner = models.ForeignKey(User, on_delete=models.CASCADE)
    Name = models.TextField(blank=False)

class Broker(models.Model):
    Group = models.ForeignKey(Group, on_delete=models.CASCADE)
    Name = models.TextField(blank=False)
    Broker = models.TextField(blank=False)
    Branch = models.TextField(blank=False)

class Profile(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE)
    Username = models.CharField(max_length=128, blank=True)
    Firstname = models.CharField(max_length=128, blank=True)
    Lastname = models.CharField(max_length=128, blank=True)
    Email = models.EmailField(max_length=128, blank=True)
    Birthday=models.DateField(auto_now=False, null=True, blank=True)