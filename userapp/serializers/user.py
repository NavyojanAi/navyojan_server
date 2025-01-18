from userapp.serializers.user_plans import SubscriptionPlanSerializer
from rest_framework import serializers
from userapp.models import UserScholarshipStatus,UserProfile,UserProfileScholarshipProvider,UserPreferences,UserDocuments,Questions,QuestionResponses
from django.contrib.auth.models import User
from userapp.models import UserSubscriptionInfo
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

class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = "__all__"

class QuestionResponsesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionResponses
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserDisplaySerializer()
    is_subscribed = serializers.SerializerMethodField()
    current_plan = serializers.SerializerMethodField()
    add_ons = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'user', 'phone_number', 'education_level', 'field_of_study', 'country', 'gender', 'profile_photo',
            'account_type', 'date_of_birth', 'is_email_verified', 'is_phone_number_verified', 'address',
            'city', 'state', 'pincode', 'school_college_university', 'current_academic_year', 'has_siblings',
            'number_of_siblings', 'are_siblings_pursuing_education', 'fathers_occupation', 'mothers_occupation',
            'annual_household_income', 'is_receiving_scholarships', 'add_ons', 'is_subscribed', 'current_plan',
            'fathers_name', 'mothers_name'
            ]
        read_only_fields = ['is_reviewer', 'is_host_user', 'is_subscribed', 'current_plan']
    
    def get_add_ons(self, obj):
        add_ons_data = QuestionResponses.objects.filter(content_type__model='user', object_id=obj.user.id)
        return QuestionResponsesSerializer(add_ons_data, many=True).data

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
        fields = ["user", "provider_type", "contact_person_name", "contact_email", "contact_phone_number", "website", "hosted_scholarships", "can_host_scholarships"]
    
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


