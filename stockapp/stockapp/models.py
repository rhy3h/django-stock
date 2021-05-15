from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    Owner = models.ForeignKey(User, on_delete=models.CASCADE)
    Name = models.TextField(blank=False)

class Broker(models.Model):
    Group = models.ForeignKey(Group, on_delete=models.CASCADE)
    Name = models.TextField(blank=False)
    Broker = models.TextField(blank=False)
    Branch = models.TextField(blank=False)