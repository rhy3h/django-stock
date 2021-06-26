from django.db import models
from django.contrib.auth.models import User

class BrokerGroup(models.Model):
    Owner = models.ForeignKey(User, on_delete=models.CASCADE)
    Name = models.TextField(blank=False)

class BrokerGroupItem(models.Model):
    BrokerGroup = models.ForeignKey(BrokerGroup, on_delete=models.CASCADE)
    Name = models.TextField(blank=False)
    Broker = models.TextField(blank=False)
    Branch = models.TextField(blank=False)

class StockGroup(models.Model):
    Owner = models.ForeignKey(User, on_delete=models.CASCADE)
    Name = models.TextField(blank=False)

class StockGroupItem(models.Model):
    StockGroup = models.ForeignKey(StockGroup, on_delete=models.CASCADE)
    Code = models.TextField(blank=False)
    Name = models.TextField(blank=False)