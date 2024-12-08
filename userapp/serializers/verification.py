from rest_framework import serializers
from userapp.models import Verification

class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = "__all__"
