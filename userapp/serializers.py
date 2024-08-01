from rest_framework import serializers
from .models import UserProfile, ScholarshipData, UserScholarshipsData
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'education_level', 'field_of_study', 'country']


class ScholarshipDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipData
        fields = '__all__'
        

class UserScholarshipDataSerializer(serializers.ModelSerializer):
    scholarship = ScholarshipDataSerializer()

    class Meta:
        model = UserScholarshipsData
        fields = ['scholarship', 'applied_date', 'status']