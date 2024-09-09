from userapp.models import ScholarshipData, UserScholarshipApplicationData
from userapp.models.scholarships import Category

from django.utils import timezone

from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
        
class ScholarshipDataSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = ScholarshipData
        fields = '__all__'

    def get_is_expired(self, obj):
        # Check if the 'deadline' field is less than the current date
        return obj.deadline < timezone.now().date()
                

class UserScholarshipDataSerializer(serializers.ModelSerializer):
    scholarship = ScholarshipDataSerializer()

    class Meta:
        model = UserScholarshipApplicationData
        fields = ['scholarship','user']

        
class CategoryWithScholarshipsSerializer(serializers.ModelSerializer):
    scholarships = ScholarshipDataSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']