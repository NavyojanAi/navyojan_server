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
        model = User
        fields = ["email", "first_name", "last_name"]
        read_only_fields = ["is_active", "is_staff", "username"]  # Sensitive fields are read-only


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserDisplaySerializer()

    class Meta:
        model = UserProfile
        fields = ['user','phone_number', 'education_level', 'field_of_study', 'country', 'gender','profile_photo']
    
    def validate_profile_photo(self, value):
        max_size = 5 * 1024 * 1024  # 5 MB
        if value.size > max_size:
            raise serializers.ValidationError("The profile photo size should not exceed 5 MB.")
        return value
    
    def update(self, instance, validated_data):
        # Handle nested user update
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserDisplaySerializer(instance=instance.user, data=user_data, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        return super().update(instance, validated_data)

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


