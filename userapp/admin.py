from django.contrib import admin
from userapp.models import UserScholarshipStatus,UserProfile, ScholarshipData, UserScholarshipApplicationData,Category,OTP,UserDocuments,UserPreferences,UserProfileScholarshipProvider,SubscriptionPlan,Documents,Eligibility,UserPlanTracker,Verification

class UserProfileAdmin(admin.ModelAdmin):
    # Adding fields to search
    search_fields = ['user__email', 'user__first_name','user__username']

    # Optional: Add filters for boolean fields in the right sidebar
    list_filter = ['is_reviewer', 'is_host_user']

    # Display these fields in the list view for better visibility
    list_display = ['user', 'is_reviewer', 'is_host_user']

# Registering the UserProfile model with the customized UserProfileAdmin
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(ScholarshipData)
admin.site.register(UserScholarshipApplicationData)
admin.site.register(Category)
admin.site.register(OTP)
admin.site.register(UserDocuments)
admin.site.register(UserPreferences)
admin.site.register(UserProfileScholarshipProvider)
admin.site.register(UserScholarshipStatus)
admin.site.register(SubscriptionPlan)
admin.site.register(Documents)
admin.site.register(Eligibility)
admin.site.register(UserPlanTracker)
admin.site.register(Verification)



