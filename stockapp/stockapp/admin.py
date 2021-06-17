from django.contrib import admin
from .models import *

admin.site.register(Profile)

admin.site.register(BrokerGroup)
admin.site.register(Broker)

admin.site.register(StockGroup)
admin.site.register(Stock)