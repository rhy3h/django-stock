from django.contrib import admin
from stockapp.models import *

# Register your models here.

admin.site.register(BrokerGroup)
admin.site.register(BrokerGroupItem)

admin.site.register(StockGroup)
admin.site.register(StockGroupItem)