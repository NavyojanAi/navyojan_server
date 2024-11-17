from rest_framework import serializers
from userapp.models import EmailVerification

class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = ['user', 'otp']
