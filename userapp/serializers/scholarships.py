from userapp.models import ScholarshipData, UserScholarshipApplicationData,Documents,Eligibility
from userapp.models.scholarships import Category
from django.utils import timezone
from django.contrib.auth.models import User


from rest_framework import serializers

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = '__all__'

class EligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Eligibility
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
        
class ScholarshipDataSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    is_expired = serializers.SerializerMethodField()
    document_needed = DocumentSerializer(many=True, read_only=True)
    eligibility = EligibilitySerializer(many=True, read_only=True)

    class Meta:
        model = ScholarshipData
        fields = '__all__'

    def get_is_expired(self, obj):
        # Check if the 'deadline' field is less than the current date
        return obj.deadline < timezone.now().date()
                
class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
        read_only_fields = ["is_active", "is_staff", "username"]  # Sensitive fields are read-only


class UserScholarshipDataSerializer(serializers.ModelSerializer):
    scholarship = ScholarshipDataSerializer()
    user = UserDisplaySerializer()

    class Meta:
        model = UserScholarshipApplicationData
        fields = ['scholarship','user']

        
class CategoryWithScholarshipsSerializer(serializers.ModelSerializer):
    scholarships = ScholarshipDataSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']