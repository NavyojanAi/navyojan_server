from django.contrib import admin
from userapp.models import UserScholarshipStatus,UserProfile, ScholarshipData, UserScholarshipApplicationData,Category,OTP,UserDocuments,UserPreferences,UserProfileScholarshipProvider
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(ScholarshipData)
admin.site.register(UserScholarshipApplicationData)
admin.site.register(Category)
admin.site.register(OTP)
admin.site.register(UserDocuments)
admin.site.register(UserPreferences)
admin.site.register(UserProfileScholarshipProvider)
admin.site.register(UserScholarshipStatus)

