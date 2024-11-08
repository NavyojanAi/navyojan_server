from rest_framework import serializers
from userapp.models import UserPayments

class UserPaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPayments
        fields = '__all__'
