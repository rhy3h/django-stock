from rest_framework import serializers
from stockapp.models import BrokerGroup

class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokerGroup
        fields = '__all__'
        # fields = ('id', 'song', 'singer', 'last_modify_date', 'created')