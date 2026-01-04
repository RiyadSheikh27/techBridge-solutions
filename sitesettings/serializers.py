from .models import *
from rest_framework import serializers

class contantInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = contantInfo
        fields = '__all__'
        
class RequestQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestQuote
        fields = "__all__"