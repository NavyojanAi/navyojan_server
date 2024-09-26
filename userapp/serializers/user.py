from userapp.serializers.user_plans import SubscriptionPlanSerializer
from rest_framework import serializers
from userapp.models import UserScholarshipStatus,UserProfile,UserProfileScholarshipProvider,UserPreferences,UserDocuments
from django.contrib.auth.models import User
from userapp.models import UserPlanTracker,UserSubscriptionInfo
from userapp.serializers.scholarships import ScholarshipDataSerializer,UserDisplaySerializer

class UserScholarshipStatusSerializer(serializers.ModelSerializer):
    user = UserDisplaySerializer()
    scholarship = ScholarshipDataSerializer()
    class Meta:
        model = UserScholarshipStatus
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserDisplaySerializer()
    is_subscribed = serializers.SerializerMethodField()
    current_plan = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['user', 'phone_number', 'education_level', 'field_of_study', 'country', 'gender', 'profile_photo', 'is_subscribed', 'current_plan']
        read_only_fields = ['is_reviewer', 'is_host_user', 'is_subscribed', 'current_plan']

    def get_is_subscribed(self, obj):
        return UserSubscriptionInfo(obj.user).is_subscribed()

    def get_current_plan(self, obj):
        plan = UserSubscriptionInfo(obj.user).get_current_plan()
        if plan:
            return SubscriptionPlanSerializer(plan).data
        return None

    def validate_profile_photo(self, value):
        if value:
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
    user = UserDisplaySerializer()
    class Meta:
        model = UserProfileScholarshipProvider
        fields = ["user","organisation", "org_site", "hosted_scholarships"]
    
    def update(self, instance, validated_data):
        # Handle nested user update
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserDisplaySerializer(instance=instance.user, data=user_data, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        return super().update(instance, validated_data)

class UserDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocuments
        exclude = ["user"]

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        exclude = ["user"]


