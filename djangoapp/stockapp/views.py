from stockapp.models import BrokerGroup
from stockapp.serializers import BrokerSerializer

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class BrokerViewSet(viewsets.ModelViewSet):
    queryset = BrokerGroup.objects.all()
    serializer_class = BrokerSerializer
    permission_classes = (IsAuthenticated,)