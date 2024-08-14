from rest_framework import serializers
from userapp.models import ScholarshipData, UserScholarshipApplicationData
from userapp.models.scholarships import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
        
class ScholarshipDataSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    class Meta:
        model = ScholarshipData
        fields = '__all__'
                

class UserScholarshipDataSerializer(serializers.ModelSerializer):
    scholarship = ScholarshipDataSerializer()

    class Meta:
        model = UserScholarshipApplicationData
        fields = ['scholarship','user']

        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
        
class CategoryWithScholarshipsSerializer(serializers.ModelSerializer):
    scholarships = ScholarshipDataSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']