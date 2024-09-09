from rest_framework import serializers
from userapp.models import UserProfile,UserProfileScholarshipProvider,UserPreferences,UserDocuments
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
    # user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'education_level', 'field_of_study', 'country', 'gender']

class UserProfileScholarshipProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileScholarshipProvider
        fields = ["organisation","org_site","hosted_scholarships"]

class UserDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocuments
        exclude = ["user"]

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        exclude = ["user"]


