from django.contrib import admin
from .models import Group, Broker, Profile

admin.site.register(Group)
admin.site.register(Broker)
admin.site.register(Profile)