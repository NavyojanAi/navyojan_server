from rest_framework import serializers
from .models import UserProfile, ScholarshipData
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']



class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'education_level', 'field_of_study', 'country']


class ScholarshipDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipData
        fields = '__all__'