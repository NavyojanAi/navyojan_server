from rest_framework import serializers
from userapp.models import ScholarshipData, UserScholarshipApplicationData

class ScholarshipDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipData
        fields = '__all__'
        

class UserScholarshipDataSerializer(serializers.ModelSerializer):
    scholarship = ScholarshipDataSerializer()

    class Meta:
        model = UserScholarshipApplicationData
        fields = ['scholarship','user']