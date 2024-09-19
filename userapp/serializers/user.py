from rest_framework import serializers
from userapp.models import UserScholarshipStatus,UserProfile,UserProfileScholarshipProvider,UserPreferences,UserDocuments
from django.contrib.auth.models import User

from userapp.serializers.scholarships import ScholarshipDataSerializer

class UserScholarshipStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserScholarshipStatus
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = "__all__"

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'education_level', 'field_of_study', 'country', 'gender']

class UserProfileScholarshipProviderSerializer(serializers.ModelSerializer):
    hosted_scholarships = ScholarshipDataSerializer(many=True, read_only=True)
    class Meta:
        model = UserProfileScholarshipProvider
        fields = ["organisation", "org_site", "hosted_scholarships"]

class UserDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocuments
        exclude = ["user"]

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        exclude = ["user"]


